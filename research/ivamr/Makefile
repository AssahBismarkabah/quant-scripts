.PHONY: help fetch probe

VENV := $(CURDIR)/../../.venv
PY := $(VENV)/bin/python
FETCH := $(CURDIR)/fetch_bars.py
PROBE := $(CURDIR)/run_probe.py

help:
	@printf '%s\n' \
		'IVAMR (Intraday Value Area Momentum & Mean Reversion) probe (pre-registered falsifiable test):' \
		'  make fetch    fetch + cache NQ 1-min bars from Databento (2013-11 .. 2023-12)' \
		'  make probe    run IS reproduction (gate 5) + OOS gates; write outputs/'

fetch:
	$(PY) $(FETCH)

probe:
	$(PY) $(PROBE)
