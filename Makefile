# ---------------------------------------------------------------------------
# Reproducibility Makefile for BisimulationMol
# Run `make help` for the list of targets.
# ---------------------------------------------------------------------------
PY ?= python

.PHONY: help setup public-models hpn-data hpn-validation caspots-validation external-validation analysis test figures notebook verify manuscript package clean

help:
	@echo "Targets:"
	@echo "  setup       Install Python dependencies"
	@echo "  public-models  Download and hash-check the two public GINsim models"
	@echo "  hpn-data     Download and hash-check public HPN-DREAM/CASPOTS artifacts"
	@echo "  hpn-validation  Run blind formal/data validation and mCRL2 cross-checks"
	@echo "  caspots-validation  Recompute repeated held-out RMSE in pinned conda env"
	@echo "  external-validation  Run mCRL2, public-model and exhaustive simulation validation"
	@echo "  analysis    Print per-module verdicts and diagnostics"
	@echo "  test        Run construction-ground-truth and regression tests"
	@echo "  figures     Regenerate every figure and result table"
	@echo "  notebook    Execute the analysis notebook end to end"
	@echo "  verify      Check deterministic results after regeneration"
	@echo "  manuscript  Compile the NetMAHIB Springer Nature manuscript"
	@echo "  package     Build the flat, source-only NetMAHIB submission ZIP"
	@echo "  clean       Remove regenerated figures and Python caches"

setup:
	$(PY) -m pip install -r requirements.txt

public-models:
	$(PY) scripts/fetch_public_models.py

hpn-data:
	$(PY) scripts/fetch_hpn_dream.py

hpn-validation: hpn-data
	$(PY) src/hpn_dream_validation.py

caspots-validation: hpn-data
	conda run -n bisimulationmol-hpn \
		python scripts/run_caspots_hpn_validation.py --repeats 2

external-validation: public-models
	$(PY) src/public_validation.py
	$(PY) src/simulation_oracle.py

analysis:
	$(PY) src/concurrent_biomodels.py

test:
	$(PY) -m unittest discover -s tests -v

figures: public-models hpn-data
	$(PY) make_figures.py

notebook:
	$(PY) -m jupyter nbconvert --to notebook --execute --inplace \
		notebooks/metodologia_multiescala.ipynb

# Elapsed-time measurements are machine-dependent. All model structures,
# relation outcomes and other result tables remain byte-level checks.
verify: test figures
	@echo "Checking that tracked deterministic results are unchanged..."
	@git diff --exit-code -- results ':(exclude)results/scalability_runtime.csv' \
		&& echo "OK: deterministic results regenerated identically." \
		|| { echo "ERROR: deterministic results changed after regeneration."; exit 1; }

manuscript:
	cd paper/netmahib && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

package: figures manuscript
	$(PY) scripts/build_netmahib_package.py

clean:
	rm -f figs/*.png
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
