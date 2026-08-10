.PHONY: help fetch probe

VENV := $(CURDIR)/../../.venv
PY := $(VENV)/bin/python
FETCH := $(CURDIR)/fetch_mvrv_data.py
PROBE := $(CURDIR)/run_probe.py

help:
	@printf '%s\n' \
		'Bitcoin MVRV Smart DCA probe:' \
		'  make fetch    download Coin Metrics CapMVRVCur + price (2010-present) into cache/' \
		'  make probe    run the pre-registered IS/OOS dynamic-vs-DCA-vs-buyhold test; write outputs/'

fetch:
	$(PY) $(FETCH)

probe:
	$(PY) $(PROBE)
