.PHONY: help probe

VENV := $(CURDIR)/../../.venv
PY := $(VENV)/bin/python
PROBE := $(CURDIR)/run_probe.py

help:
	@printf '%s\n' \
		'Short Vol / VRP candidate - v1 unconditional variance-risk-premium probe:' \
		'  make probe    run v1 probe (VIX^2 vs forward realized var on SPY, IS/OOS, bootstrap); write outputs/v1_summary.json'

probe:
	$(PY) $(PROBE)
