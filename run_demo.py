"""
Demo runner for the SALMON learnability gap detector.

    1. Load an experiment configuration -- graph source, vectorizer settings,
       thresholds, learner profiles, and the test path -- from a JSON file.
    2. Load the competency graph and fit the TF-IDF vectorizer.
    3. For each learner profile, run evaluate_path against the test path.
    4. Print a readable, fully-traceable loss report, including the regime
       shape at each step so the basis expansion is visible.

Usage:
    python run_demo.py <path/to/experiment.json>
"""

import argparse
import json
import os
import sys

from salmon_gap import (
    build_background_regime,
    build_vectorizer,
    evaluate_path,
    load_graph_from_dir,
)

# Every experiment setting (graph source, vectorizer flags, thresholds, learner
# profiles, and the test path) lives in the JSON config passed on the command
# line, so a run is fully reproducible from one file.
HERE = os.path.dirname(os.path.abspath(__file__))

# --- ANSI styling ----------------------------------------------------------
# Colors are emitted only to an interactive terminal and suppressed when piped
# or when NO_COLOR is set (https://no-color.org), so grepping the output stays
# clean. ``--no-color`` forces them off regardless.
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
GREY = "\033[90m"


def _supports_color() -> bool:
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


_COLOR_ENABLED = _supports_color()


def paint(text: str, *codes: str) -> str:
    """Wrap *text* in the given ANSI codes, unless color is disabled."""
    if not _COLOR_ENABLED or not codes:
        return text
    return f"{''.join(codes)}{text}{RESET}"


DECISION_GLYPH = {
    "LEARNABLE": "[OK]    LEARNABLE   ",
    "EXPAND_BASIS": "[+]    EXPAND_BASIS",
    "TYPED_HALT": "[HALT] TYPED_HALT  ",
}

DECISION_COLOR = {
    "LEARNABLE": GREEN,
    "EXPAND_BASIS": YELLOW,
    "TYPED_HALT": RED,
}


def fmt_shape(shape: tuple[int, int]) -> str:
    return f"({shape[0]:>2}, {shape[1]:>3})"


def print_profile_report(result: dict) -> None:
    name = result["profile_name"]
    bar = paint("=" * 78, CYAN)
    print(f"\n{bar}")
    print(f"{paint('PROFILE:', BOLD, CYAN)} {paint(name, BOLD)}")
    print(bar)

    for step in result["trace"]:
        color = DECISION_COLOR[step.decision]
        glyph = paint(DECISION_GLYPH[step.decision], BOLD, color)
        title = paint(f'"{step.competency_title}"', ITALIC, GREY)
        print(
            f"\n  {paint(f'step {step.position_in_path}', DIM)}: "
            f"{paint(step.competency_id, BOLD)}  {title}"
        )
        print(
            f"    {glyph}  {paint('residual', DIM)} = "
            f"{paint(f'{step.scalar_residual:.4f}', BOLD, color)}   "
            f"{paint('regime', DIM)} {paint(fmt_shape(step.regime_shape_before), DIM)} "
            f"{paint('->', DIM)} {paint(fmt_shape(step.regime_shape_after), DIM)}"
        )
        if step.decision in ("LEARNABLE", "EXPAND_BASIS"):
            if step.top_influences:
                print(f"    {paint('most influential priors (cosine | coeff):', DIM)}")
                for rank, (cid, cos, coeff) in enumerate(step.top_influences):
                    cid_style = (BOLD, CYAN) if rank == 0 else (CYAN,)
                    inf_title = paint(f'"{TITLE_LOOKUP.get(cid, "")}"', ITALIC, GREY)
                    print(
                        f"        {paint('-', DIM)} {paint(cid, *cid_style)}  {inf_title}"
                        f"   {paint('cos=', DIM)}{paint(f'{cos:.4f}', GREEN)}"
                        f"  {paint(f'coeff={coeff:+.4f}', DIM)}"
                    )
            else:
                print(
                    f"    {paint('most influential prior:', DIM)} "
                    f"{paint('(none — empty regime)', DIM)}"
                )
        if step.decision == "TYPED_HALT":
            gap_color = {"TYPE_1": RED, "TYPE_2": YELLOW}[step.gap_type]
            gap_label = {
                "TYPE_1": "TYPE_1 (undeclared prerequisite - no node in graph)",
                "TYPE_2": "TYPE_2 (unacquired prerequisite - node exists)",
            }[step.gap_type]
            print(f"    {paint('gap:', DIM)} {paint(gap_label, BOLD, gap_color)}")
            if step.candidate_node:
                cand_title = paint(f'"{TITLE_LOOKUP.get(step.candidate_node, "")}"', ITALIC, GREY)
                print(
                    f"    {paint('candidate prerequisite to acquire first:', DIM)} "
                    f"{paint(step.candidate_node, BOLD, CYAN)}  {cand_title}"
                )
            print(f"    {paint('missing terms (the named gap):', DIM)}")
            for term, weight in step.missing_terms:
                print(
                    f"        {paint('-', DIM)} {paint(f'{term:<18}', CYAN)} "
                    f"{paint(f'{weight:+.4f}', DIM)}"
                )

    # Summary classification.
    acquired = [s.competency_id for s in result["trace"] if s.decision == "LEARNABLE"]
    expanded = [s.competency_id for s in result["trace"] if s.decision == "EXPAND_BASIS"]
    halted = [s.competency_id for s in result["trace"] if s.decision == "TYPED_HALT"]

    print(f"\n  {paint('---- summary ----', BOLD, UNDERLINE)}")
    print(f"    {paint('acquired cleanly (LEARNABLE):', DIM)} {paint(str(acquired or '-'), GREEN)}")
    print(f"    {paint('acquired via EXPAND_BASIS   :', DIM)} {paint(str(expanded or '-'), YELLOW)}")
    print(f"    {paint('blocked (TYPED_HALT)        :', DIM)} {paint(str(halted or '-'), RED)}")
    print(
        f"    {paint('final regime shape          :', DIM)} "
        f"{paint(fmt_shape(result['final_regime_shape']), BOLD)}"
    )


def load_experiment(config_path: str) -> dict:
    """Read the JSON experiment configuration."""
    with open(config_path, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a SALMON learnability experiment from a JSON config."
    )
    parser.add_argument(
        "config",
        help="path to the experiment JSON "
        "(graph, vectorizer, thresholds, profiles, test_path)",
    )
    parser.add_argument(
        "--no-color", action="store_true", help="disable ANSI colors in the output"
    )
    args = parser.parse_args()

    if args.no_color:
        global _COLOR_ENABLED
        _COLOR_ENABLED = False

    cfg = load_experiment(args.config)

    graph_dir = os.path.join(HERE, cfg["graph"]["dir"])
    graph = load_graph_from_dir(
        graph_dir,
        definition_subdir=cfg["graph"].get("definition_subdir"),
        strip_keywords=cfg["graph"].get("strip_keywords", True),
    )

    global TITLE_LOOKUP
    TITLE_LOOKUP = {cid: node["title"] for cid, node in graph.items()}

    vec_cfg = cfg.get("vectorizer", {})
    all_defs = [node["definition"] for node in graph.values()]
    vectorizer = build_vectorizer(
        all_defs,
        use_idf=vec_cfg.get("use_idf", False),
        stop_words=vec_cfg.get("stop_words", "english"),
        lemmatize=vec_cfg.get("lemmatize", True),
    )

    thr = cfg["thresholds"]
    low, high, sim = thr["low"], thr["high"], thr["similarity"]
    test_path = cfg["test_path"]
    profiles = cfg["profiles"]

    # Optional acquisition noise: perturb each acquired vector before it enters
    # the regime, so the learner stores an imperfect representation. Absent or
    # level 0 -> a perfect learner (no noise).
    noise_cfg = cfg.get("noise", {})
    noise_level = noise_cfg.get("level", 0.0)
    seed = noise_cfg.get("seed")

    # Optional sparse memory: store only each acquired medium's top-K coefficients
    # (zeroing the rest). Absent -> store the full vector.
    acq_cfg = cfg.get("acquisition", {})
    top_k_coef = acq_cfg.get("top_k_coef")

    # Optional generic background regime: vectorized 20 newsgroups posts prepended
    # to every learner's regime as a non-specific starting subspace. Absent -> none.
    bg_cfg = cfg.get("background")
    background_regime = None
    background_ids = None
    if bg_cfg:
        source = bg_cfg.get("source", "20newsgroups")
        if source != "20newsgroups":
            raise ValueError(f"unknown background source: {source!r}")
        background_regime, background_ids = build_background_regime(
            vectorizer,
            n_docs=bg_cfg.get("n_docs", 20),
            seed=bg_cfg.get("seed", 0),
            categories=bg_cfg.get("categories"),
        )
        for bid in background_ids:
            TITLE_LOOKUP[bid] = "(20newsgroups background)"

    exp_name = cfg.get("name", os.path.basename(args.config))
    print(f"{paint('Experiment:', DIM)} {paint(exp_name, BOLD, CYAN)}")
    print(
        f"{paint('Loaded', DIM)} {paint(str(len(graph)), BOLD)} "
        f"{paint('competency nodes from', DIM)} {paint(graph_dir, GREY)}"
    )
    print(
        f"{paint('Vocabulary size:', DIM)} {paint(str(len(vectorizer.vocabulary_)), BOLD)} "
        f"{paint('terms', DIM)}"
    )
    print(
        f"{paint('Thresholds', DIM)} -> {paint('LEARNABLE', GREEN)} < {paint(str(low), BOLD)} "
        f"<= {paint('EXPAND_BASIS', YELLOW)} < {paint(str(high), BOLD)} "
        f"<= {paint('TYPED_HALT', RED)}   ({paint('sim', DIM)} >= {paint(str(sim), BOLD)})"
    )
    noise_disp = paint(str(noise_level), BOLD, MAGENTA if noise_level else "")
    print(
        f"{paint('Acquisition noise', DIM)} -> level {noise_disp} "
        f"({paint('seed', DIM)} {paint(str(seed), BOLD)})"
    )
    if background_ids is not None:
        print(
            f"{paint('Background regime', DIM)} -> "
            f"{paint(str(len(background_ids)), BOLD, MAGENTA)} 20newsgroups docs "
            f"({paint('seed', DIM)} {paint(str(bg_cfg.get('seed', 0)), BOLD)})"
        )
    if top_k_coef:
        print(
            f"{paint('Acquisition memory', DIM)} -> top-"
            f"{paint(str(top_k_coef), BOLD, MAGENTA)} coef {paint('(rest zeroed)', DIM)}"
        )
    print(f"{paint('Test path:', DIM)} {paint(str(test_path), GREY)}")

    for profile_name, known in profiles.items():
        learner = {"profile_name": profile_name, "known_competency_ids": known}
        result = evaluate_path(
            test_path,
            learner,
            graph,
            vectorizer,
            low_threshold=low,
            high_threshold=high,
            similarity_threshold=sim,
            noise_level=noise_level,
            seed=seed,
            background_regime=background_regime,
            background_ids=background_ids,
            top_k_coef=top_k_coef,
        )
        print_profile_report(result)

    print()


if __name__ == "__main__":
    main()
