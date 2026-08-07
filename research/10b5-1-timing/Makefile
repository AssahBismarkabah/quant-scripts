.PHONY: help harvest study

VENV := $(CURDIR)/../../.venv
PY := $(VENV)/bin/python
HARVEST := $(CURDIR)/harvest_adoptions.py
STUDY := $(CURDIR)/run_study.py

help:
	@printf '%s\n' \
		'10b5-1 adoption-timing probe (pre-registered falsifiable test):' \
		'  make harvest    build the 10b5-1 repurchase-adoption 8-K event set (EDGAR)' \
		'  make study      run the bounded event study + pre-registered gates'

harvest:
	$(PY) $(HARVEST) --start 2025-07-01 --end 2026-07-31

study:
	$(PY) $(STUDY)
