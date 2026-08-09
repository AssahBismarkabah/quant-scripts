.PHONY: help probe

VENV := $(CURDIR)/../../.venv
PY := $(VENV)/bin/python
PROBE := $(CURDIR)/run_probe.py

help:
	@printf '%s\n' \
		'Opening-Range / Gap trio probe (ORB, Gap Fill, Oops) — pre-registered falsifiable test:' \
		'  make probe    run IS reproduction + OOS gates on each strategy; write outputs/' \
		'Data note: reads the already-owned NQ 1-min caches from research/ivamr/cache and' \
		'research/nq-vwap-pullback/cache (no new Databento fetch required, see spec §8).'

probe:
	$(PY) $(PROBE)
