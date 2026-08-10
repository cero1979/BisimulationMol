# JMCS baseline audit

Audit date: 2026-08-10

## Repository state

- Source commit: `6d711231070a65cd121d31fd55b19f05e788fc8a`
- Working branch created for the revision: `codex/jmcs-revision`
- Pre-existing working-tree changes retained: removal of `microtype` from
  `paper/netmahib/main.tex` and an untracked NetMAHIB cover-letter DOCX.
- Principal manuscript: `paper/netmahib/main.tex`
- Bibliography: `paper/netmahib/references.bib`
- Figure sources used by the manuscript: `figs/Fig1.pdf` through `figs/Fig8.pdf`,
  with paired panels `Fig2a/Fig2b`, `Fig5a/Fig5b`, `Fig6a/Fig6b`, and
  `Fig7a/Fig7b`.
- Computational sources: `src/`, `scripts/`, `make_figures.py`, and
  `notebooks/metodologia_multiescala.ipynb`.
- Deterministic tabular outputs: `results/`.
- Regression tests: `tests/`.

## Baseline compilation

Command, run from `paper/netmahib/`:

```sh
latexmk -C main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

- Exit status: 0.
- PDF: 23 A4 pages.
- Figures: 8 numbered figures (including multi-panel figures).
- Tables: 8 numbered tables.
- Undefined citations/references: none.
- Placeholders (`???`, `TODO`, `FIXME`, `PLACEHOLDER`): none.
- Fatal LaTeX errors: none.
- Warnings: underfull boxes at the locations preserved in
  `audit/jmcs_baseline/netmahib_main.log.txt`; no overfull boxes were reported.
- Raw build records: `audit/jmcs_baseline/latexmk.stdout` and
  `audit/jmcs_baseline/netmahib_main.log.txt`.

Toolchain observed:

- Python 3.11.8
- latexmk 4.67
- pdfTeX 1.40.21 (TeX Live 2020)

## Baseline tests

Command:

```sh
python -m unittest discover -s tests -v
```

Result: 25 tests discovered; 23 passed, 1 skipped, and 1 errored. The skipped
public-model cross-check and the HPN-DREAM error have the same environmental
cause: the optional mCRL2 executable `ltscompare` was not found and
`MCRL2_LTSCOMPARE` was not set. The error occurs before any scientific result is
recomputed. Full output is in `audit/jmcs_baseline/tests.stdout`.

This baseline is therefore reproducible for the Python-native analyses but not
yet a clean one-command reproduction of the external mCRL2 checks on this host.

## Regeneration commands identified

The repository Makefile exposes the following relevant targets:

```sh
make external-validation
make hpn-validation
make holmes-pn-gdda
make figures
make test
make notebook
```

Additional targets include `make public-models`, `make hpn-data`,
`make caspots-validation`, `make pn-gdda`, `make analysis`, `make verify`, and
`make manuscript`. The JMCS revision must preserve these workflows or document
any journal-specific replacement.

## Results held invariant

The following reported values must not change without a documented regeneration
and scientific explanation:

- Synthetic benchmark: weak bisimulation 6/6, trace equality 5/6, LTS-GDA 4/6,
  structural profile 3/6, and PN-GDDA 2/6.
- Independent dual simulation-game audit: 67,600 ordered pairs within the stated
  one- and two-state finite LTS universe.
- Python/mCRL2 agreement on the reported strong and weak decisions.
- PN-GDDA catalogue: 151 graphlets, 592 orbit slots, and 576
  automorphism-distinct orbit-sensitivity cases.
- Independent PN-GDDA score agreement with Holmes to 12 decimal places.
- HPN-DREAM/LTS-GDA association: Spearman rho = 0.669 and exact p = 0.097.
- CASPOTS native-cell specificity: not established, exact p = 0.25.
- All model counts, state counts, hashes, sample sizes, and negative findings
  represented in tracked result artifacts.

## Baseline risks to address

1. The manuscript uses the Springer Nature class rather than the supplied JMCS
   class.
2. Its narrative begins with the biological application instead of the formal
   comparison problem expected for JMCS.
3. Definitions and fixed-point claims are not yet presented as a self-contained
   mathematical framework with proofs.
4. The bibliography must be audited entry by entry and rendered alphabetically
   in JMCS style.
5. The mCRL2 dependency is not discoverable on this host, so the optional test
   path and installation documentation need to be made internally consistent.
6. JMCS's mandatory `Declaration of AI Use` and a human-review log are absent.
