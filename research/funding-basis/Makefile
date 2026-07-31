PYTHON ?= python3

TEST_DIR ?= ../../tests
SYMBOL ?= BTCUSDT
INTERVAL ?= 1h
DOTENV ?= ../../.env

.PHONY: help test funding mark spot

help:
	@printf '%s\n' \
		'Funding-basis edge workflow:' \
		'  make test' \
		'  make funding SYMBOL=BTCUSDT' \
		'  make mark SYMBOL=BTCUSDT INTERVAL=1h' \
		'  make spot SYMBOL=BTCUSDT INTERVAL=1h'

test:
	$(PYTHON) -m unittest discover -s $(TEST_DIR) -q

funding:
	$(PYTHON) -m quant_scripts.funding_basis.cli --mode funding --symbol $(SYMBOL) --dotenv $(DOTENV)

mark:
	$(PYTHON) -m quant_scripts.funding_basis.cli --mode mark --symbol $(SYMBOL) --interval $(INTERVAL) --dotenv $(DOTENV)

spot:
	$(PYTHON) -m quant_scripts.funding_basis.cli --mode spot --symbol $(SYMBOL) --interval $(INTERVAL) --dotenv $(DOTENV)
