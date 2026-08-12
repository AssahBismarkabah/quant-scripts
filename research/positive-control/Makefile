.PHONY: help test-a test-b run gate

VENV := $(CURDIR)/../..//.venv
PY := $(VENV)/bin/python

help:
	@printf '%s\n' \
		'Step 1 positive-control harness verification:' \
		'  make test-a    Test A (LOAD-BEARING): synthetic embedded-alpha retrieval' \
		'  make test-b    Test B (smoke): long-equity-vs-cash premium detection' \
		'  make run       run both' \
		'  make gate      show Test A + Test B verdicts'

test-a:
	$(PY) step1_testA.py

test-b:
	$(PY) step1_testB.py

run: test-a test-b

gate:
	@printf 'Test A: '; .venv/bin/python -c "import json;print(json.load(open('step1_testA_summary.json'))['testA_verdict'])"
	@printf 'Test B: '; .venv/bin/python -c "import json;print(json.load(open('step1_testB_summary.json'))['testB_verdict'])"
