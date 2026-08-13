#!/usr/bin/env python3
"""Validate the JBCB abstract constraints in a LaTeX manuscript."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FORBIDDEN = {
    "citation": re.compile(r"\\cite[a-zA-Z*]*\s*(?:\[[^]]*\]\s*)?\{"),
    "equation environment": re.compile(r"\\begin\s*\{(?:equation|align|displaymath|gather|multline)\*?\}"),
    "display math": re.compile(r"\\\["),
    "URL": re.compile(r"\\url\s*\{"),
}


def extract_abstract(source: str) -> str:
    match = re.search(
        r"\\begin\s*\{abstract\}(.*?)\\end\s*\{abstract\}",
        source,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError("abstract environment not found")
    return match.group(1)


def plain_text(latex: str) -> str:
    latex = re.sub(r"(?<!\\)%.*", " ", latex)
    latex = re.sub(r"\\(?:emph|textit|textbf|mathrm|mathbf|mathcal|operatorname)\s*\{([^{}]*)\}", r" \1 ", latex)
    latex = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^]]*\])?", " ", latex)
    latex = latex.replace("~", " ")
    latex = re.sub(r"[{}$^_]", " ", latex)
    latex = re.sub(r"--+", "-", latex)
    return re.sub(r"\s+", " ", latex).strip()


def count_words(latex: str) -> int:
    text = plain_text(latex)
    return len(re.findall(r"\b[\w]+(?:[-'][\w]+)*\b", text, flags=re.UNICODE))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manuscript", type=Path)
    args = parser.parse_args()

    try:
        source = args.manuscript.read_text(encoding="utf-8")
        abstract = extract_abstract(source)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2

    words = count_words(abstract)
    violations = [name for name, pattern in FORBIDDEN.items() if pattern.search(abstract)]
    print(f"Abstract words: {words}")
    if words > 199:
        print("ERROR: JBCB requires fewer than 200 abstract words.")
    for violation in violations:
        print(f"ERROR: abstract contains {violation}.")
    return 1 if words > 199 or violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
