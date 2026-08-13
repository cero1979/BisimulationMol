#!/usr/bin/env python3
"""Report common British spellings in JBCB manuscript prose."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REPLACEMENTS = {
    "behaviour": "behavior",
    "behaviours": "behaviors",
    "behavioural": "behavioral",
    "labelled": "labeled",
    "labelling": "labeling",
    "modelling": "modeling",
    "modelled": "modeled",
    "normalised": "normalized",
    "normalisation": "normalization",
    "organisation": "organization",
    "organisations": "organizations",
    "emphasise": "emphasize",
    "emphasised": "emphasized",
    "catalogue": "catalog",
    "catalogues": "catalogs",
    "colour": "color",
    "colours": "colors",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manuscript", type=Path)
    args = parser.parse_args()

    try:
        lines = args.manuscript.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        print(f"ERROR: {exc}")
        return 2

    found = 0
    pattern = re.compile(r"\b(" + "|".join(map(re.escape, REPLACEMENTS)) + r")\b", re.IGNORECASE)
    for number, raw_line in enumerate(lines, start=1):
        line = re.sub(r"(?<!\\)%.*", "", raw_line)
        for match in pattern.finditer(line):
            word = match.group(0)
            print(f"{args.manuscript}:{number}: {word} -> {REPLACEMENTS[word.lower()]}")
            found += 1
    print(f"British-spelling findings: {found}")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
