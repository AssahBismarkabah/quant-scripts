.PHONY: help acquire probe1 probe2 probe3

VENV := $(CURDIR)/../../.venv
PY := $(VENV)/bin/python
ACQ := $(CURDIR)/acquire_etp.py
ACQV3 := $(CURDIR)/acquire_v3.py
P1 := $(CURDIR)/run_probe.py
P2 := $(CURDIR)/run_probe_v2.py
P3 := $(CURDIR)/run_probe_v3.py

help:
	@printf '%s\n' \
		'Short Vol / VRP candidate - DISCONFIRMED probes:' \
		'  make acquire   fetch free short/long-vol ETP daily series (SVXY/VXX/SVIX, Yahoo) into cache/' \
		'  make acquire3  fetch CBOE VIX/VIX3M/VIX9D official CDN series into cache/' \
		'  make probe1    run V1: unconditional VRP level (VIX^2 vs fwd realized var); outputs/v1_summary.json' \
		'  make probe2    run V2: tradeable short-vol (SVXY) incl. tail; outputs/v2_summary.json' \
		'  make probe3    run V3: tail-overlay short-vol (stress signals); outputs/v3_summary.json'

acquire:
	$(PY) $(ACQ)

acquire3:
	$(PY) $(ACQV3)

probe1:
	$(PY) $(P1)

probe2:
	$(PY) $(P2)

probe3:
	$(PY) $(P3)
