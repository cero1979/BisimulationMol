# JBCB Template Audit

Date: 2026-08-13

## Provenance

The author supplied `/Users/cero/Downloads/jbcb-2e.zip`, SHA-256
`109e65863c359088bf5ade74ea24254671db48d29b09d375158abbadc695c080`.
The archive identifies `ws-jbcb.tex` as dated 2026-05-18 and the rendered
instructions as dated 2026-06-11. The imported class declares:

```text
2026/05/18 v1.5g Standardized LaTeX document class
```

Imported files remain byte-identical to the supplied archive:

| file | SHA-256 |
|---|---|
| `paper/jbcb/ws-jbcb.cls` | `2cbd45997f8e62bbb5d89797bcf1c7f1c640c91fbc60282e41360d91b100a9ec` |
| `paper/jbcb/ws-jbcb.bst` | `68448e611ffb5940d03e6df8c523f2cc5606d95a67619302c59b05a0ce78f4b2` |
| `paper/jbcb/OFFICIAL_TEMPLATE.tex` | `c009b83b4a9856fabcbb8f375ea7b6a392f77d58a373a56543d68e856d2b0916` |
| `paper/jbcb/OFFICIAL_TEMPLATE.pdf` | `fe917985655c54e0c544c8156c69eed6ddca591dfb7740cd2e365383472a4631` |

## Requirements extracted from the supplied template

- Use `\documentclass{ws-jbcb}` without changing the class or bibliography
  style.
- Manuscripts use American English and 10 pt Times in a 5-inch text block.
- Abstract: fewer than 200 words, no references, URLs, or displayed equations.
- Title: preferably no more than three rendered lines.
- References: numbered by first appearance and cited as superscripts after
  punctuation, using `\usepackage[super]{cite}` and `ws-jbcb.bst`.
- Figures: Arabic numbering, placed near first mention, caption below, and
  legible after reduction. The class supports `\alttext`.
- Tables: Arabic numbering, caption above through the native `\tbl` construct.
- The class already defines `theorem`, `lemma`, `proposition`, `definition`,
  `example`, `remark`, and `proof`; `amsthm` must not be added.
- Research Paper allowance: 15 reformatted pages; the template states US$40 for
  each additional page.
- ORCID is encouraged, not mandatory. No ORCID is available in the supplied
  metadata, so none will be invented or printed.
- Publisher history and catchline fields are editorial metadata and will not be
  populated with invented dates.

## Online policy check

The current World Scientific journal pages were checked on 2026-08-13. Direct
automated access was blocked by Cloudflare, so the supplied 2026 template is the
authoritative formatting source for this revision. The journal scope visible in
indexed publisher metadata covers technical methods and tools for analysis of
cellular information, consistent with a computational biology method paper.

AI disclosure is not specified in the supplied JBCB template. It is therefore
tracked separately in `AI_DISCLOSURE_QUERY_JBCB.md` pending an author decision
after checking the publisher ethics policy.
