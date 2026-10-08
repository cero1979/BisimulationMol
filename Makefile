# Reproducibility targets for the accepted Journal of Bioinformatics and
# Computational Biology article. Use PY=/path/to/python to select an interpreter.
PY ?= python

.PHONY: help setup public-models hpn-data test gim-interface analysis \
 external-validation formal-audit death-receptor death-receptor-word \
 hpn-validation caspots-validation pn-gdda holmes-pn-gdda figures \
 notebook verify manuscript package

help:
	@echo "test                  Scientific and Journal artifact regression tests"
	@echo "public-models hpn-data Verify the included public inputs"
	@echo "death-receptor        Regenerate the main case and exact witnesses"
	@echo "death-receptor-word   Independent mCRL2 sustained-word check"
	@echo "formal-audit          Independent directional, hierarchy and exhaustive audits"
	@echo "external-validation   mCRL2 public/synthetic controls and simulation oracle"
	@echo "gim-interface         Regenerate the three-interface GIM comparison"
	@echo "hpn-validation        Exploratory held-out formal/data comparison"
	@echo "caspots-validation    Repeat held-out scores in the separate Conda environment"
	@echo "pn-gdda               Direct graphlet catalog and native-net scores"
	@echo "holmes-pn-gdda         Independent Holmes reference score (JDK/network needed)"
	@echo "figures               Supporting experiments and the six Journal figures"
	@echo "verify                Full regeneration and strict scientific-result comparison"
	@echo "notebook              Execute the canonical experiment notebook"
	@echo "manuscript / package  Clean-build Journal PDFs and the flat Journal.zip"

setup:
	$(PY) -m pip install -r requirements.txt

public-models:
	$(PY) scripts/fetch_public_models.py
	$(PY) scripts/fetch_branching_models.py

hpn-data:
	$(PY) scripts/fetch_hpn_dream.py

test:
	$(PY) -m unittest discover -s tests -v

gim-interface:
	$(PY) src/gim_interface_analysis.py

analysis:
	$(PY) src/concurrent_biomodels.py

external-validation: public-models
	$(PY) src/public_validation.py
	$(PY) src/simulation_oracle.py

formal-audit:
	$(PY) -m src.formal_audit
	$(PY) scripts/run_formal_external_audit.py

death-receptor: public-models
	$(PY) scripts/run_branching_cases.py

death-receptor-word:
	$(PY) scripts/run_death_receptor_external_audit.py --sustained-word-only

hpn-validation: hpn-data
	$(PY) src/hpn_dream_validation.py

caspots-validation: hpn-data
	conda run -n bisimulationmol-hpn python scripts/run_caspots_hpn_validation.py --repeats 2

pn-gdda:
	$(PY) -m src.pn_gdda

holmes-pn-gdda:
	$(PY) scripts/validate_holmes_pn_gdda.py

figures: public-models hpn-data gim-interface
	$(PY) make_figures.py
	$(PY) scripts/make_gim_figure.py
	$(PY) scripts/make_death_receptor_figure.py

notebook:
	$(PY) -m jupyter nbconvert --to notebook --execute --inplace \
		notebooks/metodologia_multiescala.ipynb

# Only timings and declared search-progress counters are machine-dependent.
verify: test figures formal-audit death-receptor death-receptor-word
	$(PY) scripts/verify_result_reproducibility.py

manuscript:
	$(PY) scripts/build_journal.py

package: manuscript
