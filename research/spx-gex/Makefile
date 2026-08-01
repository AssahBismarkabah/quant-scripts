PYTHON ?= python3
export PYTHONPATH := ../../src:$(PYTHONPATH)

TEST_DIR ?= ../../tests

.PHONY: help test smoke template backtest walk-forward point-template bars-template sessions-template csv-template normalize-cboe fetch-spy-bars

help:
	@printf '%s\n' \
		'SPX GEX research workflow:' \
		'  make smoke' \
		'  make template' \
		'  make point-template' \
		'  make bars-template' \
		'  make sessions-template' \
		'  make csv-template' \
		'  make normalize-cboe INPUT=...' \
		'  make fetch-spy-bars START=... END=... OUTPUT=...' \
		'  make backtest INPUT=... POINT=... BARS=...' \
		'  make walk-forward INPUT=...' \
		'  make test'

smoke:
	$(PYTHON) -m quant_scripts.spx_gex --mode smoke

template:
	$(PYTHON) -m quant_scripts.spx_gex --mode template

point-template:
	$(PYTHON) -m quant_scripts.spx_gex --mode point-template

bars-template:
	$(PYTHON) -m quant_scripts.spx_gex --mode bars-template

sessions-template:
	$(PYTHON) -m quant_scripts.spx_gex --mode sessions-template

csv-template:
	$(PYTHON) -m quant_scripts.spx_gex --mode csv-template

normalize-cboe:
	$(PYTHON) -m quant_scripts.spx_gex --mode normalize-cboe --input $(INPUT)

fetch-spy-bars:
	$(PYTHON) -m quant_scripts.spx_gex --mode fetch-spy-bars --dataset $(DATASET) --symbol $(SYMBOL) --start $(START) --end $(END) --output $(OUTPUT)

backtest:
	$(PYTHON) -m quant_scripts.spx_gex --mode backtest --point $(POINT) --bars $(BARS) --output $(OUTPUT)

walk-forward:
	$(PYTHON) -m quant_scripts.spx_gex --mode walk-forward --input $(INPUT) --output $(OUTPUT)

test:
	$(PYTHON) -m unittest discover -s $(TEST_DIR) -q
