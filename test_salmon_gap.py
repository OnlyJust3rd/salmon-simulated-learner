"""
Assertion-based checks for the SALMON gap detector. No pytest dependency:

    .venv/bin/python test_salmon_gap.py

Covers every mdl_gate level (LEARNABLE / EXPAND_BASIS / TYPED_HALT), both gap
types, the empty-regime edge case, basis growth, and the loss-report contract.
Calibrated to the 10-node database curriculum in ./competencies.

These regression checks pin the vectorizer to the *plain* tokenizer
(``lemmatize=False``): the residual bands and the 0.90/0.96 thresholds below were
hand-calibrated against that representation. WordNet lemmatization (the library
default, exercised separately by ``test_lemmatizer``) deliberately merges
morphological variants, which compresses the residual band and erases the
knife-edge EXPAND_BASIS-vs-TYPED_HALT separation this corpus was tuned to show.
"""

import numpy as np

from salmon_gap import (
    LemmaTokenizer,
    apply_top_k_memory,
    build_regime,
    build_vectorizer,
    compute_residual,
    evaluate_path,
    get_top_missing_terms,
    load_graph_from_dir,
    mdl_gate,
    search_existing_nodes,
)

GRAPH = load_graph_from_dir("competencies")
VEC = build_vectorizer([n["definition"] for n in GRAPH.values()], lemmatize=False)

# Thresholds tuned to this prose corpus (see run_demo.py for the rationale).
LOW, HIGH, SIM = 0.90, 0.96, 0.10


def test_graph_loaded():
    assert len(GRAPH) == 10
    assert set(GRAPH) == {f"comp_{i:03d}" for i in range(1, 11)}
    # frontmatter + body both parsed
    assert GRAPH["comp_001"]["title"] == "Understand the relational model"
    assert "relational" in GRAPH["comp_001"]["definition"]
    print("ok: 10 database competencies loaded with metadata + definitions")


def test_mdl_gate_boundaries():
    assert mdl_gate(0.0, LOW, HIGH) == "LEARNABLE"
    assert mdl_gate(0.89, LOW, HIGH) == "LEARNABLE"
    assert mdl_gate(0.90, LOW, HIGH) == "EXPAND_BASIS"   # low boundary -> EXPAND
    assert mdl_gate(0.95, LOW, HIGH) == "EXPAND_BASIS"
    assert mdl_gate(0.96, LOW, HIGH) == "TYPED_HALT"     # high boundary -> HALT
    assert mdl_gate(1.0, LOW, HIGH) == "TYPED_HALT"
    # thresholds are parameters, not constants
    assert mdl_gate(0.5, low_threshold=0.4, high_threshold=0.6) == "EXPAND_BASIS"
    print("ok: mdl_gate boundaries + tunable thresholds")


def test_empty_regime_full_residual():
    """A novice can reconstruct nothing -> residual is the whole vector (norm 1)."""
    regime = build_regime([], GRAPH, VEC)
    assert regime.shape[0] == 0
    vec = VEC.transform([GRAPH["comp_003"]["definition"]])
    scalar, resid = compute_residual(vec, regime)
    assert abs(scalar - 1.0) < 1e-9
    assert resid.shape[0] == len(VEC.vocabulary_)
    print("ok: empty regime yields full (norm 1.0) residual")


def test_self_reconstruction_is_zero():
    """A competency already in the regime reconstructs perfectly (residual 0)."""
    regime = build_regime(["comp_008"], GRAPH, VEC)
    vec = VEC.transform([GRAPH["comp_008"]["definition"]])
    scalar, _ = compute_residual(vec, regime)
    assert scalar < 1e-9
    assert mdl_gate(scalar, LOW, HIGH) == "LEARNABLE"
    print("ok: known competency reconstructs to ~0 residual -> LEARNABLE")


def test_learnable_near_duplicate():
    """A paraphrase of a known competency sits in the LEARNABLE band."""
    graph = dict(GRAPH)
    graph["comp_dup"] = {
        "title": "Restate the relational model",
        "miller_level": "knows",
        "parent_skill": "skill_database_foundations",
        "definition": (
            "A relational database stores data in tables of rows and columns. "
            "Each row is a tuple and each column is an attribute drawn from a "
            "domain. A schema describes the tables and their relationships. A "
            "primary key identifies a row in a table."
        ),
    }
    vec = build_vectorizer([n["definition"] for n in graph.values()], lemmatize=False)
    regime = build_regime(["comp_001"], graph, vec)
    scalar, _ = compute_residual(vec.transform([graph["comp_dup"]["definition"]]), regime)
    assert mdl_gate(scalar, LOW, HIGH) == "LEARNABLE", scalar
    print(f"ok: paraphrase of comp_001 is LEARNABLE (residual={scalar:.3f})")


def test_gap_type_2_points_at_real_prerequisite():
    """A learner without transactions hitting concurrency: gap -> comp_007 (TYPE_2)."""
    known = ["comp_001", "comp_002"]
    regime = build_regime(known, GRAPH, VEC)
    _, resid = compute_residual(VEC.transform([GRAPH["comp_008"]["definition"]]), regime)
    terms = get_top_missing_terms(resid, VEC)
    gap_type, cand = search_existing_nodes(
        terms, GRAPH, VEC, similarity_threshold=SIM, exclude_ids=set(known) | {"comp_008"}
    )
    assert gap_type == "TYPE_2" and cand == "comp_007", (gap_type, cand)
    print("ok: concurrency gap routes to TYPE_2 -> comp_007 (transactions)")


def test_gap_type_1_when_prerequisite_already_known():
    """Same concurrency target, but the learner already has transactions (comp_007).

    The only thing left unexplained is the concurrency-specific primitive
    (lock / deadlock / serializability), which no other node declares -> TYPE_1.
    This is the showcase: identical competency, different gap type by profile.
    """
    known = ["comp_001", "comp_002", "comp_003", "comp_006", "comp_007"]
    regime = build_regime(known, GRAPH, VEC)
    _, resid = compute_residual(VEC.transform([GRAPH["comp_008"]["definition"]]), regime)
    terms = get_top_missing_terms(resid, VEC)
    gap_type, cand = search_existing_nodes(
        terms, GRAPH, VEC, similarity_threshold=SIM, exclude_ids=set(known) | {"comp_008"}
    )
    assert gap_type == "TYPE_1" and cand is None, (gap_type, cand)
    print("ok: concurrency gap is TYPE_1 once transactions are already known")


def test_basis_grows_only_on_acquisition():
    """LEARNABLE/EXPAND_BASIS add a regime row; TYPED_HALT does not."""
    learner = {
        "profile_name": "backend_engineer",
        "known_competency_ids": ["comp_001", "comp_002", "comp_003", "comp_006", "comp_007"],
    }
    result = evaluate_path(
        ["comp_003", "comp_009", "comp_008"], learner, GRAPH, VEC,
        low_threshold=LOW, high_threshold=HIGH, similarity_threshold=SIM,
    )
    # comp_003 LEARNABLE (already known) + comp_009 EXPAND_BASIS -> 5 known grows to 7
    assert result["final_regime_shape"][0] == 7
    acquired = [s.competency_id for s in result["trace"]
                if s.decision in ("LEARNABLE", "EXPAND_BASIS")]
    halted = [s for s in result["trace"] if s.decision == "TYPED_HALT"]
    assert acquired == ["comp_003", "comp_009"]
    assert {s.competency_id for s in halted} == {"comp_008"}
    for s in halted:  # halts leave the regime shape unchanged
        assert s.regime_shape_before == s.regime_shape_after
    print("ok: basis grows on acquisition, frozen on TYPED_HALT")


def test_lemmatizer():
    """The NLP pipeline lemmatizes (POS-aware) and drops stopwords."""
    tok = LemmaTokenizer(stop_words={"a", "the", "is", "are", "of", "in", "and"})
    out = tok("Databases are storing queries and running indexes in the tables")
    # plurals + verb forms collapse to their lemma; stopwords are gone
    assert "database" in out and "databases" not in out
    assert "query" in out and "queries" not in out
    assert "run" in out and "running" not in out
    assert "table" in out and "tables" not in out
    assert "the" not in out and "are" not in out

    # End to end: lemmatization merges morphological variants into one vocab term,
    # so the lemmatized vocabulary is strictly smaller than the plain one.
    defs = [n["definition"] for n in GRAPH.values()]
    plain = build_vectorizer(defs, lemmatize=False)
    lemma = build_vectorizer(defs, lemmatize=True)
    assert len(lemma.vocabulary_) < len(plain.vocabulary_)
    # "tables" and "table" are distinct plain features but the same lemma feature
    assert {"table", "tables"} <= set(plain.get_feature_names_out())
    lemma_feats = set(lemma.get_feature_names_out())
    assert "table" in lemma_feats and "tables" not in lemma_feats
    print("ok: lemmatizer normalizes variants + removes stopwords, shrinks vocab")


def test_top_k_memory():
    """Storing top-K coefficients keeps exactly K terms (the strongest), unit norm."""
    vec = VEC.transform([GRAPH["comp_001"]["definition"]])
    dense = np.asarray(vec.todense()).ravel()
    k = 5
    rng = np.random.default_rng(0)

    # noise-free: exactly the top-k clean terms, renormalized to unit length
    stored = apply_top_k_memory(vec, rng, 0.0, k)
    sd = np.asarray(stored.todense()).ravel()
    assert np.count_nonzero(sd) == k
    assert abs(np.linalg.norm(sd) - 1.0) < 1e-9
    expected = set(np.argsort(np.abs(dense))[::-1][:k])
    assert set(np.nonzero(sd)[0]) == expected

    # with noise: still exactly K nonzeros -- the zeroed terms stay zero
    noisy = apply_top_k_memory(vec, rng, 0.5, k)
    nd = np.asarray(noisy.todense()).ravel()
    assert np.count_nonzero(nd) == k
    assert set(np.nonzero(nd)[0]) == expected
    print("ok: top-k memory keeps exactly k strongest terms, unit norm")


def test_loss_report_contract():
    """The loss report matches the documented schema."""
    learner = {"profile_name": "novice", "known_competency_ids": []}
    result = evaluate_path(
        ["comp_003", "comp_009", "comp_008"], learner, GRAPH, VEC,
        low_threshold=LOW, high_threshold=HIGH, similarity_threshold=SIM,
    )
    required = {
        "type", "competency_id", "competency_title", "position_in_path",
        "scalar_residual", "missing_terms", "gap_type", "candidate_node", "signal",
    }
    assert len(result["loss_report"]) == 3  # novice halts on all three
    for entry in result["loss_report"]:
        assert required <= set(entry), set(entry)
        assert entry["type"] == "TYPED_HALT"
        assert entry["gap_type"] in ("TYPE_1", "TYPE_2")
        assert isinstance(entry["missing_terms"], list)
        if entry["gap_type"] == "TYPE_1":
            assert entry["candidate_node"] is None
        else:
            assert entry["candidate_node"] in GRAPH
    print("ok: loss report matches documented schema")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("\nall checks passed")
