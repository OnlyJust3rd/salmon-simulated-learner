"""
inspect_data.py -- a CLI to look at separate details of the SALMON medium corpus.

Each subcommand surfaces one view of the data the validator actually vectorizes
(the same loader and vectorizer used by run_demo / salmon_gap).

Subcommands:
    top-coef   For every medium, show its highest TF-IDF coefficients.

Usage:
    python inspect_data.py top-coef -k 10
    python inspect_data.py top-coef -k 5 --idf
    python inspect_data.py top-coef --no-color | less
"""

import argparse
import os
import sys

import numpy as np

from salmon_gap import build_vectorizer, load_graph_from_dir

HERE = os.path.dirname(os.path.abspath(__file__))

# --- ANSI styling ----------------------------------------------------------
# Colors only to an interactive terminal; suppressed when piped or NO_COLOR is
# set (https://no-color.org). ``--no-color`` forces them off.
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
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


def _load_vectorized(args) -> tuple[list[str], dict, "np.ndarray", object]:
    """Load the medium corpus and fit/transform it -> (ids, graph, X, vectorizer)."""
    graph = load_graph_from_dir(
        os.path.join(HERE, args.dir),
        definition_subdir=args.mediums,
        strip_keywords=not getattr(args, "keep_keywords", False),
    )
    ids = list(graph)
    definitions = [graph[cid]["definition"] for cid in ids]
    vectorizer = build_vectorizer(definitions, use_idf=args.idf)
    matrix = vectorizer.transform(definitions)
    return ids, graph, matrix, vectorizer


def _bar(weight: float, peak: float, width: int = 18) -> str:
    """A proportional block bar, full at the document's own peak weight."""
    if peak <= 0:
        return ""
    return "█" * max(1, round(width * weight / peak))


def cmd_top_coef(args) -> None:
    ids, graph, matrix, vectorizer = _load_vectorized(args)
    terms = vectorizer.get_feature_names_out()

    weighting = "tf-idf" if args.idf else "tf (no idf)"
    print(
        f"{paint('Corpus:', DIM)} {paint(str(len(ids)), BOLD)} mediums from "
        f"{paint(os.path.join(args.dir, args.mediums), GREY)}"
    )
    print(
        f"{paint('Vectorizer:', DIM)} {paint(weighting, BOLD)}, lemmatized, "
        f"english stopwords  {paint('|', DIM)} "
        f"{paint(str(len(vectorizer.vocabulary_)), BOLD)} {paint('vocab terms', DIM)}"
    )
    print(f"{paint(f'Top {args.k} coefficients per document:', BOLD)}\n")

    for i, cid in enumerate(ids):
        row = matrix.getrow(i)
        if row.nnz == 0:
            continue
        order = np.argsort(row.data)[::-1][: args.k]
        peak = float(row.data[order[0]])

        title = paint(f'"{graph[cid]["title"]}"', ITALIC, GREY)
        print(f"{paint(cid, BOLD, CYAN)}  {title}")
        for rank, j in enumerate(order, start=1):
            term = terms[row.indices[j]]
            weight = float(row.data[j])
            print(
                f"  {paint(f'{rank:>2}.', DIM)} {paint(f'{term:<20}', CYAN)} "
                f"{paint(f'{weight:.4f}', BOLD, GREEN)}  "
                f"{paint(_bar(weight, peak), YELLOW)}"
            )
        print()


def build_parser() -> argparse.ArgumentParser:
    # Shared options usable either before or after the subcommand. SUPPRESS keeps
    # the subparser copy from clobbering a value given before the subcommand.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--no-color",
        action="store_true",
        default=argparse.SUPPRESS,
        help="disable ANSI colors in the output",
    )

    parser = argparse.ArgumentParser(
        description="Inspect details of the SALMON medium corpus.",
        parents=[common],
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_top = sub.add_parser(
        "top-coef",
        parents=[common],
        help="show each medium's highest TF-IDF coefficients",
    )
    p_top.add_argument(
        "-k", "--k", type=int, default=10, help="how many top terms per document (default 10)"
    )
    p_top.add_argument("--dir", default="paths/1", help="graph dir (default paths/1)")
    p_top.add_argument(
        "--mediums", default="mediums", help="definitions subdir (default mediums)"
    )
    p_top.add_argument(
        "--idf", action="store_true", help="weight with IDF (default: plain term frequency)"
    )
    p_top.add_argument(
        "--keep-keywords",
        action="store_true",
        help="do not strip each node's keyword terms before vectorizing",
    )
    p_top.set_defaults(func=cmd_top_coef)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if getattr(args, "no_color", False):
        global _COLOR_ENABLED
        _COLOR_ENABLED = False

    args.func(args)


if __name__ == "__main__":
    main()
