"""
SALMON learnability gap detector
=================================

A graph validator that answers one question:

    Given a learner's current knowledge state and a target competency,
    does the learning path contain a *gap* -- a competency whose concept
    load cannot be reconstructed from what the learner already knows?

Theoretical basis: Residual-Adequacy Architecture
(Amornbunchornvej 2026, arxiv 2605.24999).

    - The learner's knowledge state is a REGIME: a matrix whose rows are
      TF-IDF vectors of the definitions of the competencies they already know.
    - A new competency arrives as a TF-IDF vector.
    - We project it onto the subspace spanned by the regime rows (least squares).
    - The scalar residual = how much of the new competency CANNOT be
      reconstructed from the current subspace.
        * residual LOW  -> learnable; stack the vector as a new regime row
                            (basis expansion) and continue.
        * residual HIGH -> typed halt; the residual vector points at exactly
                            the terms that live outside the learner's subspace.
                            Those named terms ARE the gap.

Every decision is traceable to a specific term and a scalar value.

Dependencies: numpy, scipy, scikit-learn, nltk (for lemmatization).
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field

import numpy as np
from scipy.sparse import csr_matrix, vstack
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------------------------
# Graph loading
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def parse_competency_md(text: str) -> dict:
    """Parse one competency markdown file: YAML-ish frontmatter + body.

    The body (everything after the closing ``---``) is the *definition*
    used for vectorization. Frontmatter carries the structured metadata.
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError("competency file missing '---' frontmatter block")
    raw_meta, body = m.group(1), m.group(2)

    meta: dict = {}
    for line in raw_meta.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip()

    # keywords are a JSON array in the frontmatter, e.g. ["database", "table"]
    raw_keywords = meta.get("keywords", "")
    try:
        keywords = json.loads(raw_keywords) if raw_keywords else []
        if not isinstance(keywords, list):
            keywords = []
    except (json.JSONDecodeError, TypeError):
        keywords = []

    # normalize whitespace in the definition body
    definition = " ".join(body.split())
    return {
        "title": meta.get("title", ""),
        "miller_level": meta.get("miller_level", ""),
        "parent_skill": meta.get("parent_skill", ""),
        "keywords": keywords,
        "definition": definition,
    }


def remove_keywords(text: str, keywords: list[str]) -> str:
    """Strip a node's own keyword terms from its definition before vectorizing.

    Without this, a medium that explains "relational database" is saturated with
    the very phrase that names the outcome, so its vector matches the term
    trivially rather than the surrounding concepts. We remove each keyword phrase
    case-insensitively, word-boundaried, tolerating a simple trailing plural "s"
    (so "primary key" also catches "primary keys"). Longer phrases are removed
    first so a multi-word keyword is taken out whole before its component words.
    """
    for kw in sorted((k.strip() for k in keywords), key=len, reverse=True):
        if not kw:
            continue
        words = re.split(r"\s+", kw)
        pattern = r"\b" + r"\s+".join(re.escape(w) for w in words) + r"s?\b"
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)
    return " ".join(text.split())


def load_graph_from_dir(
    path: str,
    definition_subdir: str | None = None,
    strip_keywords: bool = True,
) -> dict:
    """Load every ``*.md`` in *path* into a SALMON graph dict.

    Returns ``{competency_id: {title, miller_level, parent_skill, keywords,
    definition}}``. The competency id is taken from the filename stem.

    By default each node's ``definition`` is the body of its own markdown file.
    When *definition_subdir* is given, the definition is instead read from
    ``<path>/<definition_subdir>/<stem>.md`` (parsed the same way, taking its
    body) while the title, keywords, and metadata still come from the node file.
    This lets terse outcome nodes carry their rich teaching prose in a sibling
    folder. If a node has no matching file in the subdir, it falls back to its
    own body.

    When *strip_keywords* is true (the default), each node's own keyword terms
    are removed from its definition before it is returned, so the medium is not
    contaminated by the very term it defines (see ``remove_keywords``).
    """
    graph: dict = {}
    for fname in sorted(os.listdir(path)):
        if not fname.endswith(".md"):
            continue
        comp_id = os.path.splitext(fname)[0]
        with open(os.path.join(path, fname), encoding="utf-8") as fh:
            node = parse_competency_md(fh.read())

        if definition_subdir is not None:
            medium_path = os.path.join(path, definition_subdir, fname)
            if os.path.isfile(medium_path):
                with open(medium_path, encoding="utf-8") as fh:
                    node["definition"] = parse_competency_md(fh.read())["definition"]

        if strip_keywords and node["keywords"]:
            node["definition"] = remove_keywords(node["definition"], node["keywords"])

        graph[comp_id] = node
    return graph


# ---------------------------------------------------------------------------
# NLP preprocessing (tokenize -> POS-tag -> lemmatize -> drop stopwords)
# ---------------------------------------------------------------------------

# Resources the lemmatizer needs, paired with the nltk.data.find path used to
# detect whether they are already present (so we only hit the network once).
_NLTK_RESOURCES = {
    "wordnet": "corpora/wordnet",
    "omw-1.4": "corpora/omw-1.4",
    "averaged_perceptron_tagger_eng": "taggers/averaged_perceptron_tagger_eng",
}

# Penn Treebank tag (first letter) -> WordNet POS. Giving the lemmatizer the
# right part of speech is what turns "running" into "run" rather than leaving it
# unchanged; unknown tags default to noun.
_TREEBANK_TO_WORDNET = {"J": "a", "V": "v", "N": "n", "R": "r"}


def _ensure_nltk_data() -> None:
    """Download the WordNet + POS-tagger corpora once, quietly, if missing."""
    import nltk

    for resource, find_path in _NLTK_RESOURCES.items():
        try:
            nltk.data.find(find_path)
        except LookupError:
            nltk.download(resource, quiet=True)


class LemmaTokenizer:
    """A TfidfVectorizer ``tokenizer`` that lemmatizes with WordNet.

    Pipeline per document: regex-tokenize (2+ char word tokens) -> POS-tag with
    the averaged-perceptron tagger -> WordNet-lemmatize each token under its POS
    -> drop stopwords. Sharing one normalization across the whole corpus is what
    collapses morphological variants (tables/table, stores/storing/stored,
    queries/query) onto a single vocabulary term, which tightens the genuine
    overlap between related definitions and sharpens the SALMON residual signal.
    """

    _token_re = re.compile(r"\b\w\w+\b")

    def __init__(self, stop_words: set[str] | None = None) -> None:
        _ensure_nltk_data()
        from nltk.stem import WordNetLemmatizer
        from nltk.tag import PerceptronTagger

        self._lemmatizer = WordNetLemmatizer()
        self._tagger = PerceptronTagger()
        self._stop_words = stop_words or set()

    def __call__(self, doc: str) -> list[str]:
        tokens = self._token_re.findall(doc.lower())
        out: list[str] = []
        for word, tag in self._tagger.tag(tokens):
            pos = _TREEBANK_TO_WORDNET.get(tag[:1], "n")
            lemma = self._lemmatizer.lemmatize(word, pos)
            if lemma not in self._stop_words:
                out.append(lemma)
        return out


# ---------------------------------------------------------------------------
# Core functions (numbered per the spec)
# ---------------------------------------------------------------------------

def build_vectorizer(
    all_competency_definitions: list[str],
    use_idf: bool = False,
    stop_words: str | list[str] | None = "english",
    lemmatize: bool = True,
) -> TfidfVectorizer:
    """(1) Fit a TF-IDF vectorizer on the full corpus of definitions.

    Vectors are L2-normalized (sklearn default) so that a lone competency
    vector has norm 1.0 -- this keeps residual norms on a comparable,
    tunable scale across the whole graph: residual**2 == 1 - ||projection||**2,
    so a residual is literally "the fraction of concept load left unexplained."

    ``use_idf`` is exposed as a knob. With IDF *on*, shared scaffolding terms
    are down-weighted, which on small graphs drives almost everything to a
    residual of ~1.0 (vectors become near-orthogonal). With IDF *off* the
    representation is normalized term frequency, so genuine vocabulary overlap
    between a new competency and the regime actually reconstructs -- which is
    what makes the LEARNABLE / EXPAND_BASIS gradient observable. Default off.

    ``stop_words`` drops filler words. With prose (multi-sentence) definitions,
    function words like "the", "a", "of" otherwise appear in every node and
    create spurious overlap that collapses every residual toward zero. Default
    "english"; pass ``None`` for terse keyword-bag definitions.

    ``lemmatize`` (default on) runs the NLP preprocessing pipeline -- WordNet
    lemmatization via :class:`LemmaTokenizer` -- so morphological variants share
    one vocabulary term. Stopword removal then happens inside the tokenizer on
    the lemmatized tokens, so it is set on the vectorizer as ``None`` to avoid a
    double pass. Pass ``lemmatize=False`` for plain sklearn tokenization.
    """
    if lemmatize:
        if stop_words == "english":
            sw = set(ENGLISH_STOP_WORDS)
        elif stop_words:
            sw = set(stop_words)
        else:
            sw = set()
        vectorizer = TfidfVectorizer(
            norm="l2",
            use_idf=use_idf,
            tokenizer=LemmaTokenizer(sw),
            token_pattern=None,
            stop_words=None,
        )
    else:
        vectorizer = TfidfVectorizer(norm="l2", use_idf=use_idf, stop_words=stop_words)
    vectorizer.fit(all_competency_definitions)
    return vectorizer


def build_regime(
    known_competency_ids: list[str],
    graph: dict,
    vectorizer: TfidfVectorizer,
) -> csr_matrix:
    """(2) Stack the TF-IDF vectors of known competencies into the regime matrix.

    Returns a sparse matrix of shape ``(n_known, vocab_size)``. An empty
    knowledge state (beginner) yields a ``(0, vocab_size)`` matrix -- a
    subspace of dimension zero, against which everything is residual.
    """
    vocab_size = len(vectorizer.vocabulary_)
    if not known_competency_ids:
        return csr_matrix((0, vocab_size))
    definitions = [graph[cid]["definition"] for cid in known_competency_ids]
    return vectorizer.transform(definitions)


def build_background_regime(
    vectorizer: TfidfVectorizer,
    n_docs: int = 20,
    seed: int = 0,
    categories: list[str] | None = None,
) -> tuple[csr_matrix, list[str]]:
    """Sample posts from the 20 newsgroups corpus as a generic background regime.

    The sampled posts are vectorized with the *already-fitted* ``vectorizer`` so
    they live in the same vocabulary space as the competency mediums, then serve
    as starting rows prepended to every learner's regime -- a generic "background
    knowledge" subspace, an alternative to seeding the regime with a specific node
    such as L1-noise. Posts that vectorize to all-zero in the competency
    vocabulary (no shared terms) are dropped. ``seed`` makes the random sample
    reproducible.

    Returns ``(matrix (m, V), ids)`` where ids are synthetic labels like
    ``"20news#1234"`` naming each sampled post.
    """
    from sklearn.datasets import fetch_20newsgroups

    data = fetch_20newsgroups(
        subset="train", categories=categories, remove=("headers", "footers", "quotes")
    )
    rng = np.random.default_rng(seed)
    n = min(n_docs, len(data.data))
    sampled = rng.choice(len(data.data), size=n, replace=False)
    matrix = vectorizer.transform([data.data[int(i)] for i in sampled])
    # drop posts with no overlap with the competency vocabulary (zero vector)
    norms = np.asarray(matrix.multiply(matrix).sum(axis=1)).ravel()
    keep = np.where(norms > 0)[0]
    matrix = matrix[keep]
    ids = [f"20news#{int(sampled[j])}" for j in keep]
    return matrix, ids


def compute_residual(
    new_competency_vector: csr_matrix,
    regime_matrix: csr_matrix,
) -> tuple[float, np.ndarray]:
    """(3) Project *new_competency_vector* onto the regime subspace.

    The regime rows are the basis. We solve, in least-squares sense,

        regime.T @ coeffs ~= new_vector

    so the reconstruction lives in span(regime rows). The residual is what
    the current subspace cannot represent.

    Returns ``(scalar_residual, residual_vector)`` where ``scalar_residual``
    is the L2 norm of the dense residual vector.
    """
    new_dense = np.asarray(new_competency_vector.todense()).ravel()

    # Empty regime: nothing to project onto -> the whole vector is residual.
    if regime_matrix.shape[0] == 0:
        return float(np.linalg.norm(new_dense)), new_dense

    # A = basis matrix with one column per known competency (vocab_size, n_known)
    A = np.asarray(regime_matrix.todense()).T
    coeffs, *_ = np.linalg.lstsq(A, new_dense, rcond=None)
    reconstruction = A @ coeffs
    residual_vector = new_dense - reconstruction
    scalar_residual = float(np.linalg.norm(residual_vector))
    return scalar_residual, residual_vector


def rank_regime_influences(
    new_competency_vector: csr_matrix,
    regime_matrix: csr_matrix,
    regime_ids: list[str],
    n: int = 3,
) -> list[tuple[str, float, float]]:
    """Rank the prior regime mediums by how much they explain *new_competency_vector*.

    For each regime row (a competency the learner already knows / has acquired)
    we report two complementary signals, computed against the regime *before* the
    new medium is stacked in:

      - ``cosine`` -- the cosine similarity between the new medium and that prior;
        the intuitive "what you already know that this is most like."
      - ``coefficient`` -- that row's least-squares weight in the same projection
        ``compute_residual`` performs (``reconstruction = A @ coeffs``); the
        literal contribution that drove the residual down.

    Results are aggregated per competency id, since one medium can occupy several
    regime rows (a prior the learner knows that is also re-acquired along the
    path, possibly as a noisy copy): its ``cosine`` is the best of those rows and
    its ``coefficient`` is their sum (the medium's total reconstruction share).

    Returns ``[(competency_id, cosine, coefficient), ...]`` for the top-``n``
    distinct mediums by cosine. An empty regime yields ``[]`` (nothing to build on
    yet).
    """
    if regime_matrix.shape[0] == 0:
        return []
    new_dense = np.asarray(new_competency_vector.todense()).ravel()
    cosines = cosine_similarity(new_competency_vector, regime_matrix).ravel()
    A = np.asarray(regime_matrix.todense()).T
    coeffs, *_ = np.linalg.lstsq(A, new_dense, rcond=None)

    best_cos: dict[str, float] = {}
    sum_coeff: dict[str, float] = {}
    for i, cid in enumerate(regime_ids):
        c = float(cosines[i])
        if cid not in best_cos or c > best_cos[cid]:
            best_cos[cid] = c
        sum_coeff[cid] = sum_coeff.get(cid, 0.0) + float(coeffs[i])
    ranked = sorted(best_cos, key=lambda cid: best_cos[cid], reverse=True)[:n]
    return [(cid, round(best_cos[cid], 4), round(sum_coeff[cid], 4)) for cid in ranked]


def get_top_missing_terms(
    residual_vector: np.ndarray,
    vectorizer: TfidfVectorizer,
    n: int = 10,
) -> list[tuple[str, float]]:
    """(4) Map the largest-magnitude residual dimensions back to vocabulary terms.

    These named terms are the gap: concept load the learner's current
    subspace cannot reconstruct. Returns ``[(term, weight), ...]`` sorted by
    descending magnitude, dropping ~zero entries.
    """
    terms = vectorizer.get_feature_names_out()
    magnitudes = np.abs(residual_vector)
    order = np.argsort(magnitudes)[::-1]
    out: list[tuple[str, float]] = []
    for idx in order[:n]:
        weight = float(residual_vector[idx])
        if abs(weight) < 1e-9:
            break
        out.append((terms[idx], round(weight, 4)))
    return out


def search_existing_nodes(
    missing_terms: list[tuple[str, float]],
    graph: dict,
    vectorizer: TfidfVectorizer,
    similarity_threshold: float = 0.6,
    exclude_ids: set[str] | None = None,
) -> tuple[str, str | None]:
    """(5) Classify the gap by searching for the missing concept in the graph.

    Builds a query vector from the missing terms, then takes the cosine
    similarity against every *candidate* node's definition vector.

        best match >= threshold -> ("TYPE_2", matched_node_id)
            the concept exists in the graph but is NOT in the learner's
            regime yet -> surface it as a prerequisite to acquire first.
        otherwise                -> ("TYPE_1", None)
            the concept is undeclared -- no node represents it ->
            flag for a human expert to declare the missing node.

    ``exclude_ids`` removes nodes that cannot legitimately be the answer:
    the competency currently under evaluation (it would always match itself)
    and everything already in the learner's regime (a TYPE_2 prerequisite is
    by definition something not yet acquired). Excluding them is what makes
    the search point at a *real* upstream gap instead of a tautology.
    """
    if not missing_terms:
        return ("TYPE_1", None)

    exclude_ids = exclude_ids or set()
    candidate_ids = [nid for nid in graph if nid not in exclude_ids]
    if not candidate_ids:
        return ("TYPE_1", None)

    # Build the query straight from the residual: each missing term contributes
    # its residual magnitude, so a strongly-unexplained term pulls the search
    # harder than a marginal one. (A uniform bag-of-words query would let many
    # small terms outvote the one term that actually dominates the gap.)
    vocab = vectorizer.vocabulary_
    query_vec = np.zeros(len(vocab))
    for term, weight in missing_terms:
        if term in vocab:
            query_vec[vocab[term]] = abs(weight)
    norm = np.linalg.norm(query_vec)
    if norm == 0:
        return ("TYPE_1", None)
    query_vec = (query_vec / norm).reshape(1, -1)

    node_vecs = vectorizer.transform([graph[nid]["definition"] for nid in candidate_ids])
    sims = cosine_similarity(query_vec, node_vecs).ravel()

    best_idx = int(np.argmax(sims))
    best_sim = float(sims[best_idx])
    if best_sim >= similarity_threshold:
        return ("TYPE_2", candidate_ids[best_idx])
    return ("TYPE_1", None)


def mdl_gate(
    scalar_residual: float,
    low_threshold: float = 0.3,
    high_threshold: float = 0.6,
) -> str:
    """(6) Minimum-description-length style gate on the scalar residual.

        residual < low                  -> "LEARNABLE"
        low <= residual < high          -> "EXPAND_BASIS"
        residual >= high                -> "TYPED_HALT"

    Thresholds are parameters, not constants, so the SALMON validator can be
    tuned per skill domain.
    """
    if scalar_residual < low_threshold:
        return "LEARNABLE"
    if scalar_residual < high_threshold:
        return "EXPAND_BASIS"
    return "TYPED_HALT"


# ---------------------------------------------------------------------------
# Path evaluation
# ---------------------------------------------------------------------------

@dataclass
class StepTrace:
    """One competency's worth of traceable decision data."""

    position_in_path: int
    competency_id: str
    competency_title: str
    scalar_residual: float
    decision: str
    regime_shape_before: tuple[int, int]
    regime_shape_after: tuple[int, int]
    missing_terms: list[tuple[str, float]] = field(default_factory=list)
    gap_type: str | None = None
    candidate_node: str | None = None
    top_influences: list[tuple[str, float, float]] = field(default_factory=list)


def apply_representation_noise(
    competency_vector: csr_matrix,
    rng: np.random.Generator,
    noise_level: float,
) -> csr_matrix:
    """Perturb an acquired competency vector before it joins the regime.

    Stacking the exact TF-IDF vector assumes the learner internalizes a new
    definition perfectly. In reality the representation they store is imperfect
    -- they re-encode the concept through their own, slightly distorted memory.
    We model that by rotating the vector by a small random amount: zero-mean
    Gaussian noise is scaled so its norm is ``noise_level`` times the vector's
    own norm (so ``noise_level`` is the fractional perturbation, roughly the
    rotation angle in radians), then the result is renormalized to unit length.
    A seeded ``rng`` keeps the perturbation reproducible across runs.

    ``noise_level <= 0`` returns the vector unchanged -- a perfect learner.
    """
    if noise_level <= 0:
        return competency_vector.copy()
    dense = np.asarray(competency_vector.todense()).ravel()
    signal_norm = float(np.linalg.norm(dense))
    if signal_norm == 0.0:
        return competency_vector.copy()
    noise = rng.standard_normal(dense.shape)
    noise *= noise_level * signal_norm / np.linalg.norm(noise)
    perturbed = dense + noise
    perturbed /= np.linalg.norm(perturbed)
    return csr_matrix(perturbed)


def apply_top_k_memory(
    competency_vector: csr_matrix,
    rng: np.random.Generator,
    noise_level: float,
    k: int,
) -> csr_matrix:
    """Store only the strongest ``k`` coefficients of a medium -- a sparse memory.

    Stacking the full vector assumes the learner retains every term of a
    definition. More realistically they keep only its most salient concepts, so
    we keep the top-``k`` coefficients (by magnitude) of the *clean* definition
    and zero the rest. If ``noise_level > 0``, zero-mean Gaussian noise is then
    added to *only those k retained dimensions* -- scaled so its norm is
    ``noise_level`` times the kept signal's norm, exactly as
    ``apply_representation_noise`` does, but confined to the support so the zeroed
    terms stay zero. The result is renormalized to unit length.

    ``k`` is clamped to the number of nonzero terms; ``noise_level <= 0`` gives a
    pure (noise-free) truncation.
    """
    dense = np.asarray(competency_vector.todense()).ravel()
    nonzero = int(np.count_nonzero(dense))
    if nonzero == 0:
        return competency_vector.copy()
    k = min(k, nonzero)

    keep = np.argsort(np.abs(dense))[::-1][:k]
    out = np.zeros_like(dense)
    out[keep] = dense[keep]

    if noise_level > 0:
        kept_norm = float(np.linalg.norm(out))
        noise = rng.standard_normal(k)
        noise *= noise_level * kept_norm / np.linalg.norm(noise)
        out[keep] += noise

    out /= np.linalg.norm(out)
    return csr_matrix(out)


def evaluate_path(
    path: list[str],
    learner: dict,
    graph: dict,
    vectorizer: TfidfVectorizer,
    low_threshold: float = 0.3,
    high_threshold: float = 0.6,
    similarity_threshold: float = 0.6,
    top_n_terms: int = 10,
    noise_level: float = 0.0,
    seed: int | None = None,
    background_regime: csr_matrix | None = None,
    background_ids: list[str] | None = None,
    top_k_coef: int | None = None,
) -> dict:
    """(7) Walk the path in order, growing the regime as competencies are acquired.

    For each competency:
        a. vectorize its definition
        b. compute the residual against the current regime
        c. run the mdl_gate on the scalar residual
        d. LEARNABLE / EXPAND_BASIS -> stack the vector as a new regime row
           (regime grows (n, V) -> (n+1, V)). With ``noise_level > 0`` the
           stored row is a noisy copy of the vector (see
           ``apply_representation_noise``), modelling imperfect internalization.
        e. TYPED_HALT -> extract missing terms, classify the gap via
           search_existing_nodes, record a loss entry, and DO NOT grow the
           regime (the learner cannot acquire this competency yet)

    ``noise_level`` and ``seed`` control the acquisition noise: the residual and
    decision are still computed against the clean incoming definition (the
    learner judges learnability correctly), but what enters the regime -- their
    memory of it -- is perturbed and reproducible for a given seed.

    ``background_regime`` / ``background_ids`` (e.g. from
    ``build_background_regime``) are prepended to the regime for every learner,
    providing a generic starting subspace independent of the profile.

    ``top_k_coef`` (if set) stores only each acquired medium's strongest ``k``
    coefficients (``apply_top_k_memory``) instead of the full vector -- a sparse,
    lossy memory. Decisions are still made on the full clean vector.

    Returns a structured result with the full per-step trace and the loss report.
    """
    known_regime = build_regime(learner["known_competency_ids"], graph, vectorizer)
    # Optional generic background subspace (e.g. vectorized 20 newsgroups posts),
    # prepended to EVERY learner's regime as a non-specific starting basis.
    if background_regime is not None and background_regime.shape[0] > 0:
        regime = (
            vstack([background_regime, known_regime])
            if known_regime.shape[0]
            else background_regime
        )
        regime_ids: list[str] = list(background_ids or []) + list(
            learner["known_competency_ids"]
        )
    else:
        regime = known_regime
        regime_ids = list(learner["known_competency_ids"])
    rng = np.random.default_rng(seed)

    # Ids whose vectors currently span the regime. A TYPE_2 prerequisite must
    # be something OUTSIDE this set, so we exclude it from the node search.
    # (Background rows are not graph nodes, so they need not appear here.)
    in_regime: set[str] = set(learner["known_competency_ids"])

    trace: list[StepTrace] = []
    loss_report: list[dict] = []

    for pos, comp_id in enumerate(path):
        comp = graph[comp_id]
        vec = vectorizer.transform([comp["definition"]])
        scalar_residual, residual_vector = compute_residual(vec, regime)
        decision = mdl_gate(scalar_residual, low_threshold, high_threshold)

        shape_before = regime.shape

        if decision in ("LEARNABLE", "EXPAND_BASIS"):
            # Which prior mediums most explain this one -- measured against the
            # regime as it stands BEFORE the new row is added.
            top_influences = rank_regime_influences(vec, regime, regime_ids)
            if top_k_coef:
                stored = apply_top_k_memory(vec, rng, noise_level, top_k_coef)
            else:
                stored = apply_representation_noise(vec, rng, noise_level)
            regime = vstack([regime, stored]) if regime.shape[0] else stored
            in_regime.add(comp_id)
            regime_ids.append(comp_id)
            shape_after = regime.shape
            trace.append(
                StepTrace(
                    position_in_path=pos,
                    competency_id=comp_id,
                    competency_title=comp["title"],
                    scalar_residual=round(scalar_residual, 4),
                    decision=decision,
                    regime_shape_before=shape_before,
                    regime_shape_after=shape_after,
                    top_influences=top_influences,
                )
            )
        else:  # TYPED_HALT
            missing_terms = get_top_missing_terms(residual_vector, vectorizer, top_n_terms)
            gap_type, candidate = search_existing_nodes(
                missing_terms,
                graph,
                vectorizer,
                similarity_threshold,
                exclude_ids=in_regime | {comp_id},
            )
            shape_after = regime.shape  # unchanged -- not acquired
            trace.append(
                StepTrace(
                    position_in_path=pos,
                    competency_id=comp_id,
                    competency_title=comp["title"],
                    scalar_residual=round(scalar_residual, 4),
                    decision=decision,
                    regime_shape_before=shape_before,
                    regime_shape_after=shape_after,
                    missing_terms=missing_terms,
                    gap_type=gap_type,
                    candidate_node=candidate,
                )
            )
            loss_report.append(
                {
                    "type": "TYPED_HALT",
                    "competency_id": comp_id,
                    "competency_title": comp["title"],
                    "position_in_path": pos,
                    "scalar_residual": round(scalar_residual, 4),
                    "missing_terms": missing_terms,
                    "gap_type": gap_type,
                    "candidate_node": candidate,
                    "signal": "concept load exceeds current regime representational scope",
                }
            )

    return {
        "profile_name": learner["profile_name"],
        "final_regime_shape": regime.shape,
        "trace": trace,
        "loss_report": loss_report,
    }
