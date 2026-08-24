.PHONY: help phase0 probe

VENV := $(CURDIR)/../../.venv
PY := $(VENV)/bin/python
PROBE := $(CURDIR)/run_probe.py

help:
	@printf '%s\n' \
		'Earnings-anchored VWAP daily proxy (frozen bounded falsification):' \
		'  make phase0   generate/evaluate the required 100-event timing audit' \
		'  make probe    run the daily IS/OOS study only after Phase 0 passes'

phase0:
	$(PY) $(PROBE) --phase0

probe:
	$(PY) $(PROBE)
