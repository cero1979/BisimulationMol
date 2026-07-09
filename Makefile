# ---------------------------------------------------------------------------
# Reproducibility Makefile for BisimulationMol
# Run `make help` for the list of targets.
# ---------------------------------------------------------------------------
PY ?= python

.PHONY: help setup analysis figures notebook verify clean

help:
	@echo "Targets:"
	@echo "  setup     Install Python dependencies (pip install -r requirements.txt)"
	@echo "  analysis  Print the per-module verdicts and diagnostics (stdout only)"
	@echo "  figures   Regenerate every figure (figs/) and table (results/)"
	@echo "  notebook  Execute the exploratory notebook end to end"
	@echo "  verify    Regenerate results/ and fail if anything changed (determinism)"
	@echo "  clean     Remove regenerated figures and Python caches"

setup:
	$(PY) -m pip install -r requirements.txt

analysis:
	$(PY) src/concurrent_biomodels.py

figures:
	$(PY) make_figures.py

notebook:
	$(PY) -m jupyter nbconvert --to notebook --execute --inplace \
		notebooks/metodologia_multiescala.ipynb

# Regenerate the tracked tables/CSVs and fail if they differ from what is
# committed. This is the one-command proof that the paper's numbers are
# reproduced bit-for-bit from the curated models (fixed random seeds).
verify: figures
	@echo "Checking that tracked results/ are unchanged after regeneration..."
	@git diff --exit-code -- results \
		&& echo "OK: results/ regenerated identically (deterministic)." \
		|| { echo "ERROR: results/ changed after regeneration."; exit 1; }

clean:
	rm -f figs/*.png
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
