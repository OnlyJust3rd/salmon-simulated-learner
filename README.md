# SALMON learnability gap detector

A prototype validator for **SALMON** (Skill-Aligned Learning Map Ontology) that
answers one question:

> Given a learner's current knowledge state and a target competency, does the
> learning path contain a **gap** — a competency whose concept load cannot be
> reconstructed from what the learner already knows?

It implements the **Residual-Adequacy Architecture**
(Amornbunchornvej 2026, arxiv 2605.24999).

## The idea in one paragraph

A learner's knowledge state is a **regime**: a matrix whose rows are TF-IDF
vectors of the definitions of the competencies they already know. A new
competency arrives as a vector; we project it onto the subspace spanned by the
regime rows (least squares) and measure the **scalar residual** — the fraction
of the new competency that the current subspace *cannot* reconstruct. Because
the vectors are L2-normalized, `residual² = 1 − ‖projection‖²`, so the residual
is literally "how much concept load is left unexplained." Low residual → the
competency is learnable, so we **stack its vector as a new regime row** (basis
expansion) and continue. High residual → a **typed halt**, and the residual
vector points at exactly the terms living outside the learner's subspace. Those
named terms *are* the gap.

## Files

| file | purpose |
|------|---------|
| `salmon_gap.py` | the validator module — all 7 core functions |
| `run_demo.py` | loads the toy graph, runs every profile, prints readable reports |
| `test_salmon_gap.py` | assertion checks (every gate level, both gap types, edges) |
| `competencies/comp_*.md` | competency nodes: frontmatter metadata + definition body |

The toy graph is a **10-node database curriculum** (`comp_001`–`comp_010`):
relational model → SQL queries → joins → aggregation → normalization → indexing
→ transactions/ACID → concurrency control → query optimization → recovery.
Each node is a 4–5 sentence prose definition.

## Run it

```bash
python3 -m venv .venv
.venv/bin/pip install numpy scipy scikit-learn nltk
.venv/bin/python run_demo.py        # readable per-profile loss reports
.venv/bin/python test_salmon_gap.py # checks
```

`nltk` powers the NLP preprocessing in `build_vectorizer` (WordNet lemmatization
+ stopword removal). The first run downloads the small WordNet and
perceptron-tagger corpora automatically; afterwards it works offline.

## The two gap types

When a competency halts, the residual's top terms are searched against every
*other* node in the graph (the competency under evaluation and everything
already in the regime are excluded — a prerequisite is by definition something
not yet acquired):

- **TYPE_2 — unacquired prerequisite.** A node above the similarity threshold
  exists. The concept is in the graph; the learner just hasn't acquired it.
  → surface it as the next thing to learn.
- **TYPE_1 — undeclared prerequisite.** Nothing matches. No node represents the
  missing concept. → flag for a human expert to declare the node.

## What the toy run demonstrates

Path: `comp_003` joins → `comp_009` query optimization → `comp_008` concurrency.
The same target competency produces *different* diagnoses depending on the
learner — which is the whole point of residual adequacy:

| competency | novice | app_developer | backend_engineer |
|---|---|---|---|
| `comp_003` joins | HALT → **TYPE_2** `comp_002` (needs SQL basics) | **LEARNABLE** (already known) | **LEARNABLE** (already known) |
| `comp_009` query optimization | HALT → **TYPE_2** `comp_003` | HALT → **TYPE_2** `comp_006` (needs indexing) | **EXPAND_BASIS** (acquired — has indexing) |
| `comp_008` concurrency control | HALT → **TYPE_2** `comp_007` (needs transactions) | HALT → **TYPE_2** `comp_007` (needs transactions) | HALT → **TYPE_1** (concurrency primitives never declared) |

Two contrasts to notice:

- **`comp_009`**: the app_developer is told "learn indexing first" (TYPE_2 →
  `comp_006`), but the backend_engineer *has* indexing, so optimization becomes
  **EXPAND_BASIS** — learnable, and the regime grows.
- **`comp_008`**: the app_developer is told "learn transactions first" (TYPE_2 →
  `comp_007`), but the backend_engineer *already has* transactions, so the only
  thing left unexplained is the concurrency-specific primitive
  (lock / deadlock / serializability) — which no node in the curriculum
  declares, yielding a **TYPE_1** flag for a human expert.

This is the residual-adequacy thesis in action: as the learner's regime grows,
the *same* competency moves from "you're missing a known prerequisite" to "the
curriculum itself has a hole."

## Tunable thresholds

All passed as parameters, never hardcoded in logic:

- `low_threshold` (0.90) / `high_threshold` (0.96) — the `mdl_gate` bands
  (`LEARNABLE` / `EXPAND_BASIS` / `TYPED_HALT`). These are calibrated to *this*
  corpus: 4–5 sentence prose definitions share only ~15–37% of their TF-IDF
  direction even between directly-related concepts, so residuals compress into a
  high band (~0.90–1.00). The absolute scale is large but the *ordering* carries
  the signal, so the boundaries sit where the corpus puts them. (The terse
  keyword-bag graph used earlier lived around 0.3 / 0.6 — re-tune per corpus.)
- `similarity_threshold` (0.10 in the demo) — TYPE_2 vs TYPE_1 cutoff. A halt's
  missing-term query is dominated by the target's own distinctive vocabulary
  (which no other node contains), so the prerequisite signal is real but small;
  a low cutoff cleanly separates "prerequisite exists" from "undeclared."
- `use_idf` (default `False`) on `build_vectorizer` — IDF down-weights shared
  scaffolding terms, which on a small graph makes vectors near-orthogonal and
  collapses the learnability gradient. Plain normalized term frequency keeps the
  gradient observable.
- `stop_words` (default `"english"`) on `build_vectorizer` — drops filler words.
  Essential for prose definitions, where "the / a / of" otherwise appear in every
  node and create spurious overlap. Pass `None` for terse keyword-bag graphs.

## Definitions live in markdown

Each competency is a `comp_*.md` file: `---`-delimited frontmatter
(`id`, `title`, `miller_level`, `parent_skill`) followed by the free-text
definition that gets vectorized. `load_graph_from_dir` parses the folder into a
SALMON graph dict. This keeps the curriculum human-editable and reviewable.
