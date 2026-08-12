.PHONY: run gate

VENV := $(CURDIR)/../..//.venv

run:
	$(VENV)/bin/python step2_basket.py

gate:
	@.venv/bin/python -c "import json;print('Step 2 verdict:',json.load(open('step2_basket_summary.json'))['step2_verdict'])"
