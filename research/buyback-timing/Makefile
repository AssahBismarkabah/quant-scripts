.PHONY: help harvest study test

VENV := $(CURDIR)/../../.venv
PY := $(VENV)/bin/python
PYTHONPATH := $(CURDIR)/../../src:$(PYTHONPATH)
export PYTHONPATH

help:
	@echo '  make harvest            harvest + classify 8-K repurchase-program events (EDGAR)'
	@echo '    HARVEST_START=..      harvest start date (default 2025-07-01)'
	@echo '    HARVEST_END=..        harvest end date (default 2026-07-31)'
	@echo '    MAX_DOCS=..           limit classified docs (dry-run / debug)'

harvest:
	$(PY) -m quant_scripts.buyback_timing harvest \
		$(if $(HARVEST_START),--start $(HARVEST_START),) \
		$(if $(HARVEST_END),--end $(HARVEST_END),) \
		$(if $(MAX_DOCS),--max-docs $(MAX_DOCS),)

test:
	$(PY) -m pytest ../../tests/test_buyback_timing.py -q
