PYTHON ?= python3
export PYTHONPATH := ../../src:$(PYTHONPATH)

TEST_DIR ?= ../../tests
SYMBOL ?= BTCUSDT
INTERVAL ?= 1h
DOTENV ?= ../../.env

.PHONY: help test smoke dump funding mark spot

help:
	@printf '%s\n' \
		'Funding-basis edge workflow:' \
		'  make smoke' \
		'  make dump SYMBOL=BTCUSDT INTERVAL=1h' \
		'  make test' \
		'  make funding SYMBOL=BTCUSDT' \
		'  make mark SYMBOL=BTCUSDT INTERVAL=1h' \
		'  make spot SYMBOL=BTCUSDT INTERVAL=1h'

smoke:
	$(PYTHON) -m quant_scripts.funding_basis.cli --mode smoke --dotenv $(DOTENV) --insecure-tls

dump:
	$(PYTHON) -m quant_scripts.funding_basis.cli --mode dump --symbol $(SYMBOL) --interval $(INTERVAL) --dotenv $(DOTENV) --insecure-tls --output-dir fixtures

test:
	$(PYTHON) -m unittest discover -s $(TEST_DIR) -q

funding:
	$(PYTHON) -m quant_scripts.funding_basis.cli --mode funding --symbol $(SYMBOL) --dotenv $(DOTENV)

mark:
	$(PYTHON) -m quant_scripts.funding_basis.cli --mode mark --symbol $(SYMBOL) --interval $(INTERVAL) --dotenv $(DOTENV)

spot:
	$(PYTHON) -m quant_scripts.funding_basis.cli --mode spot --symbol $(SYMBOL) --interval $(INTERVAL) --dotenv $(DOTENV)
