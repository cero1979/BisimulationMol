# ---------------------------------------------------------------------------
# Reproducibility Makefile for BisimulationMol
# Run `make help` for the list of targets.
# ---------------------------------------------------------------------------
PY ?= python

.PHONY: help setup public-models gim-interface hpn-data hpn-validation caspots-validation external-validation pn-gdda holmes-pn-gdda analysis test figures notebook verify manuscript package jbcb-manuscript jbcb-package jmcs-manuscript jmcs-package netmahib-manuscript netmahib-package clean

help:
	@echo "Targets:"
	@echo "  setup       Install Python dependencies"
	@echo "  public-models  Download and hash-check the two public GINsim models"
	@echo "  gim-interface  Run the three-interface GIM sensitivity analysis"
	@echo "  hpn-data     Download and hash-check public HPN-DREAM/CASPOTS artifacts"
	@echo "  hpn-validation  Run the exploratory held-out HPN analysis and mCRL2 checks"
	@echo "  caspots-validation  Recompute repeated held-out RMSE in pinned conda env"
	@echo "  external-validation  Run mCRL2, public-model and exhaustive simulation validation"
	@echo "  pn-gdda     Audit the 151/592 catalog and print direct native-net scores"
	@echo "  holmes-pn-gdda  Download/hash Holmes 1.1.1 and reproduce its reference score"
	@echo "  analysis    Print per-module verdicts and diagnostics"
	@echo "  test        Run construction-ground-truth and regression tests"
	@echo "  figures     Regenerate every figure and result table"
	@echo "  notebook    Execute the analysis notebook end to end"
	@echo "  verify      Check deterministic results after regeneration"
	@echo "  manuscript  Compile the current JBCB manuscript"
	@echo "  package     Build and verify the self-contained JBCB submission ZIP"
	@echo "  jbcb-manuscript  Compile the retained pre-R2 JBCB manuscript"
	@echo "  jbcb-package     Build the retained R1 submission ZIP"
	@echo "  jbcb-r2-audit    Recompute R2 independent quantifier/direction and mCRL2 checks"
	@echo "  jbcb-r2-package  Assemble and clean-build all flat R2 archives"
	@echo "  jbcb-r3-analysis Regenerate the fixed-interface death-receptor analysis"
	@echo "  jbcb-r3-package  Assemble and clean-build all flat R3 archives"
	@echo "  jmcs-manuscript  Compile the current JMCS manuscript explicitly"
	@echo "  jmcs-package     Build the current JMCS submission ZIP explicitly"
	@echo "  netmahib-manuscript  Compile the superseded Springer manuscript"
	@echo "  netmahib-package     Build the superseded Springer submission ZIPs"
	@echo "  clean       Remove regenerated figures and Python caches"

setup:
	$(PY) -m pip install -r requirements.txt

public-models:
	$(PY) scripts/fetch_public_models.py

gim-interface:
	$(PY) src/gim_interface_analysis.py

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

pn-gdda:
	$(PY) -m src.pn_gdda

holmes-pn-gdda:
	$(PY) scripts/validate_holmes_pn_gdda.py

analysis:
	$(PY) src/concurrent_biomodels.py

test:
	$(PY) -m unittest discover -s tests -v

figures: public-models hpn-data gim-interface
	$(PY) make_figures.py

notebook:
	$(PY) scripts/update_notebook_netmahib.py
	$(PY) -m jupyter nbconvert --to notebook --execute --inplace \
		notebooks/metodologia_multiescala.ipynb

# Run timings and bounded-search progress depend on the machine. Model
# structures, decisions, witnesses and declared limits remain strict checks.
verify: test figures jbcb-r2-audit jbcb-r3-analysis
	$(PY) scripts/verify_result_reproducibility.py

manuscript: jbcb-r3-manuscript

package: jbcb-r3-package

.PHONY: jbcb-r3-analysis jbcb-r3-manuscript jbcb-r3-package

jbcb-r3-analysis:
	$(PY) scripts/fetch_branching_models.py
	$(PY) scripts/run_branching_cases.py

jbcb-r3-manuscript:
	$(PY) scripts/make_revision_R3_figures.py
	$(PY) scripts/assemble_jbcb_R3.py
	$(PY) scripts/build_jbcb_R3_package.py

jbcb-r3-package: jbcb-r3-manuscript

.PHONY: jbcb-r2-audit jbcb-r2-manuscript jbcb-r2-package

jbcb-r2-audit:
	$(PY) -m src.formal_revision_audit
	$(PY) scripts/run_R2_external_audit.py
	$(PY) scripts/write_R2_direction_inventory.py

jbcb-r2-manuscript:
	$(PY) scripts/assemble_jbcb_R2.py
	$(PY) scripts/make_revision_R2_figures.py
	$(PY) tools/check_jbcb_abstract.py revision_R2/main_jbcb_R2.tex
	$(PY) tools/check_jbcb_english.py revision_R2/main_jbcb_R2.tex
	cd revision_R2 && latexmk -pdf -interaction=nonstopmode -halt-on-error main_jbcb_R2.tex Supplementary_Validation_R2.tex response_to_reviewer_R2.tex

jbcb-r2-package: jbcb-r2-manuscript
	$(PY) scripts/build_jbcb_R2_package.py

jbcb-manuscript:
	$(PY) tools/check_jbcb_abstract.py paper/jbcb/main_jbcb.tex
	$(PY) tools/check_jbcb_english.py paper/jbcb/main_jbcb.tex
	cd paper/jbcb && latexmk -pdf -interaction=nonstopmode -halt-on-error main_jbcb.tex

jbcb-package: jbcb-manuscript
	$(PY) scripts/build_jbcb_package.py

jmcs-manuscript:
	cd paper/jmcs && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

jmcs-package: jmcs-manuscript
	$(PY) scripts/build_jmcs_package.py

netmahib-manuscript:
	cd paper/netmahib && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

netmahib-package: figures netmahib-manuscript
	$(PY) scripts/build_netmahib_package.py

clean:
	rm -f figs/*.png
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
