VENV := $(CURDIR)/../../.venv
PYTHON := $(VENV)/bin/python
BARS := $(CURDIR)/../index-rebalancing/cache/bars/SPY.parquet

.PHONY: study help

help:
	@echo '  make study          run the flow-fade first-pass study'
	@echo '  make study OUT=path write JSON report to path'

study:
	$(PYTHON) run_study.py --bars $(BARS) $(if $(OUT),--out $(OUT),)
