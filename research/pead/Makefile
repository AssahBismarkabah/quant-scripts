.PHONY: help fetch probe

VENV := $(CURDIR)/../../.venv
PY := $(VENV)/bin/python
FETCH := $(CURDIR)/fetch_pead_data.py
PROBE := $(CURDIR)/run_probe.py

help:
	@printf '%s\n' \
		'PEAD (post-earnings-announcement drift) probe:' \
		'  make fetch    download the Kaggle earnings+price dataset (486MB zip) into cache/' \
		'  make probe    run the pre-registered IS/OOS long-short drift test; write outputs/'

fetch:
	$(PY) $(FETCH)

probe:
	$(PY) $(PROBE)
