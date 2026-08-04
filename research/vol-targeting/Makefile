VENV := $(CURDIR)/../../.venv
PYTHON := $(VENV)/bin/python
BARS := $(CURDIR)/../index-rebalancing/cache/bars/SPY.parquet
BARS_CLEAN := $(CURDIR)/cache/SPY_clean.parquet

.PHONY: study study-v1-clean study-v2 verify help

help:
	@echo '  make study          run the flow-fade first-pass study (original DB cache)'
	@echo '  make study OUT=path write JSON report to path'
	@echo '  make study-v1-clean re-run v1 study on verified clean bars'
	@echo '  make study-v2       run the revisit (v2) study with co-base cells A/B'
	@echo '  make study-v2 OUT=path write JSON report to path'
	@echo '  make verify         run v2 data validation (bars, VIXCLS, episodes)'

study:
	$(PYTHON) run_study.py --bars $(BARS) $(if $(OUT),--out $(OUT),)

study-v1-clean:
	$(PYTHON) run_study.py --bars $(BARS_CLEAN) $(if $(OUT),--out $(OUT),)

study-v2:
	$(PYTHON) run_study_v2.py $(if $(OUT),--out $(OUT),)

verify:
	$(PYTHON) verify_data.py
