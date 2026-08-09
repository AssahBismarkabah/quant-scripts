.PHONY: help acquire probe1 probe2

VENV := $(CURDIR)/../../.venv
PY := $(VENV)/bin/python
ACQ := $(CURDIR)/acquire_etp.py
P1 := $(CURDIR)/run_probe.py
P2 := $(CURDIR)/run_probe_v2.py

help:
	@printf '%s\n' \
		'Short Vol / VRP candidate - DISCONFIRMED probes:' \
		'  make acquire   fetch free short/long-vol ETP daily series (SVXY/VXX/SVIX, Yahoo) into cache/' \
		'  make probe1    run V1: unconditional VRP level (VIX^2 vs fwd realized var); outputs/v1_summary.json' \
		'  make probe2    run V2: tradeable short-vol (SVXY) incl. tail; outputs/v2_summary.json'

acquire:
	$(PY) $(ACQ)

probe1:
	$(PY) $(P1)

probe2:
	$(PY) $(P2)
