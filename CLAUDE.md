# CLAUDE.md

Onboarding notes for working in this repo. Read this first.

## What this project is

A Python prototype of **SALMON** — a *learnability gap detector* built on the
Residual-Adequacy Architecture (Amornbunchornvej 2026, arXiv 2605.24999). It
answers one question:

> Given what a learner already knows (their **regime**) and a target competency,
> can the new competency be reconstructed from what they already know — or is
> there a **gap**?

The mechanism, end to end:

1. Each competency has a prose **definition** (its "medium"). We TF-IDF–vectorize
   the definitions (L2-normalized; `use_idf=False` by default → normalized term
   frequency).
2. The learner's **regime** is a matrix whose rows are the vectors of the
   competencies they already know.
3. A new competency arrives as a vector `b`. We **least-squares project** it onto
   the span of the regime rows and measure the **residual** = `‖b − projection‖`.
   Because `b` is unit-norm, `residual = sin(angle to subspace)`, range `[0, 1]`.
4. `mdl_gate` thresholds the residual:
   - `residual < low` → **LEARNABLE** (stack the new vector as a regime row).
   - `low ≤ residual < high` → **EXPAND_BASIS** (learnable, but a stretch; the
     stored vector is added with simulated learning distortion — see below).
   - `residual ≥ high` → **TYPED_HALT** (a real gap). The residual vector points
     at the exact terms outside the learner's subspace — those named terms *are*
     the gap.
5. A halt is typed: **TYPE_2** if a graph node represents the missing concept
   (declared-but-unacquired prerequisite), **TYPE_1** if no node matches (an
   undeclared prerequisite).

## Files

- `salmon_gap.py` — the core module. All the logic lives here. Key functions:
  - `load_graph_from_dir(path, definition_subdir=None, strip_keywords=True)` —
    loads `*.md` competency nodes, keyed by filename stem; pulls the definition
    prose from the `definition_subdir` (mediums) folder; strips each node's own
    `keywords` from its definition before vectorizing (so a definition isn't
    contaminated by the very term it defines).
  - `build_vectorizer(defs, use_idf=False, stop_words="english", lemmatize=True)`
    — TF-IDF with a custom `LemmaTokenizer` (NLTK WordNet lemmatization + POS
    tagging, sklearn English stopwords).
  - `build_regime(...)`, `build_background_regime(...)` — assemble regime
    matrices; the background option samples 20newsgroups docs as a generic
    "noise floor" subspace.
  - `compute_residual(new_vec, regime)` → `(scalar_residual, residual_vector)`.
  - `rank_regime_influences(...)` — which known competencies most explain the new
    one (cosine + projection coefficient).
  - `apply_representation_noise(...)` / `apply_top_k_memory(...)` — simulate
    imperfect learning when a vector is acquired via EXPAND_BASIS (the learner
    doesn't store a perfect copy; top-K keeps only the strongest coefficients and
    adds seeded noise).
  - `mdl_gate(...)`, `evaluate_path(...)` — the gate and the per-path driver.
- `run_demo.py` — the main entry point. Reads a JSON experiment config (required
  positional arg) and prints a colored, per-profile trace of a learning path.
- `inspect_data.py` — corpus inspection CLI; `top-coef` shows each medium's
  highest TF-IDF terms.
- `test_salmon_gap.py` — plain-Python test script (run it directly; not pytest).
- `README.md` — background/theory notes.
- `paths/1/` — the active curriculum (see below).

## Running things

A `.venv` already exists (Python 3.13, with numpy/scipy/scikit-learn/nltk). Use
it directly — don't create a new one:

```bash
.venv/bin/python run_demo.py paths/1/tests/setting-3.json   # main demo
.venv/bin/python run_demo.py paths/1/tests/setting-3.json --no-color
.venv/bin/python inspect_data.py top-coef -k 8              # inspect corpus
.venv/bin/python test_salmon_gap.py                         # run tests
```

Always run the test script after changes — it should report **all checks
passed**.

## The `paths/1/` curriculum

This is where the real work is. A database-concepts DAG (`chart-detransitive.mmd`)
from `Database System` → `PostgreSQL`. Structure:

- `paths/1/L1-*.md` — competency **outcome** nodes. Frontmatter carries `id`,
  `title`, `miller_level`, `parent_skill`, and `keywords` (a JSON array of the
  terms the learner can recall after mastering the node — these are stripped from
  the definition before vectorizing). Body holds the `Criteria` line.
- `paths/1/mediums/L1-*.md` — the **definition prose** for each node (the
  "medium" the learner studies). One per outcome, matched by filename stem.
- `paths/1/tests/setting-*.json` — experiment configs: graph dir, vectorizer
  options, thresholds (`low`/`high`/`similarity`), noise, 20newsgroups
  background, `top_k_coef`, the `test_path`, and learner `profiles` (which nodes
  each profile already knows). `setting-3.json` is the current canonical one.
- `L1-highschool-it.md` and `L1-highschool-math.md` are the **baseline** mediums —
  the knowledge every educated learner is assumed to hold. The `highschool-normie`
  profile starts from these. `L1-noise.md` is filler given to every profile.

### Important gotcha: residuals live in a high, narrow band

Short prose definitions share surprisingly little TF-IDF direction even between
related concepts (~15–37%), so residuals compress into a tight `~0.85–1.00`
band, and the thresholds in each config are **calibrated to that specific
corpus**. Two consequences:

- If you change medium prose, **re-check residuals** — small wording changes move
  the numbers. Use `build_regime([...baseline...])` + `compute_residual(...)` to
  measure a node against just the baseline.
- Counterintuitively, *shortening/concentrating* a medium can **raise** its
  residual (fewer incidental shared words). Overlap comes from shared vocabulary
  with the regime, not from brevity.

A recurring task here is making a node learnable from the baseline by ensuring the
**baseline mediums carry the vocabulary** the node needs — e.g. the relation/table
concept was added to `L1-highschool-math.md`, and OS file/user/sharing vocabulary
to `L1-highschool-it.md`, so the baseline regime spans those directions. When a
node still HALTs, read the **missing terms** in the trace — they tell you exactly
which words the regime lacks.

### Known frontmatter inconsistencies (pre-existing, low priority)

- `L1-define-nosql.md` — `Criteria` still references PostgreSQL.
- `L1-recognize-sql.md` — `id` is `L1-define-sql` (title says "Define"), a leftover.

Don't fix these unless asked; they don't affect loading (nodes are keyed by
filename stem, not by frontmatter `id`).

## `competencies/` — ignore for now

The top-level `competencies/` folder (`comp_001.md` … `comp_010.md`) is an older,
separate corpus that is **not** part of the active `paths/1/` work. Leave it
alone unless explicitly asked. (The test script uses its own pinned corpus; it
does not depend on `competencies/`.)

## Working norms

- Prefer editing existing mediums/configs over adding new files.
- After any change to mediums, vectorizer, or thresholds: run `test_salmon_gap.py`
  **and** re-run the relevant `setting-*.json` to confirm the per-profile
  decisions still make sense.
- When asked to make something "learnable with no prerequisite," that usually
  means *injecting the needed vocabulary into the baseline mediums*, not weakening
  thresholds — but report residual numbers honestly; if vocabulary overlap can't
  cross the line, say so rather than gaming it.
