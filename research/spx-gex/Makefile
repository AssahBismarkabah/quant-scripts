PYTHON ?= ../../.venv/bin/python
ifneq ($(wildcard ../../.venv/bin/python),)
PYTHON := ../../.venv/bin/python
else ifneq ($(wildcard ./.venv/bin/python),)
PYTHON := ./.venv/bin/python
else
PYTHON ?= python3
endif
export PYTHONPATH := ../../src:$(PYTHONPATH)

DEFAULT_START ?= 2026-07-31T13:30:00+00:00
DEFAULT_END ?= 2026-07-31T20:00:00+00:00
TEST_DIR ?= ../../tests
DATASET ?= EQUS.MINI
SYMBOL ?= SPY
START ?=
END ?=
OUTPUT ?= /tmp/spy_bars.json
POINT ?=
BARS ?=
INPUT ?=

.DEFAULT_GOAL := fetch-spy-bars-default

.PHONY: help test smoke template backtest walk-forward point-template bars-template sessions-template csv-template normalize-cboe fetch-spy-bars

help:
	@printf '%s\n' \
		'SPX GEX research workflow:' \
		'  make' \
		'  make smoke' \
		'  make template' \
		'  make point-template' \
		'  make bars-template' \
		'  make sessions-template' \
		'  make csv-template' \
		'  make normalize-cboe INPUT=...' \
		'  make fetch-spy-bars START=... END=... OUTPUT=...' \
		'  make fetch-spy-bars-default' \
		'  make backtest POINT=... BARS=...' \
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

fetch-spy-bars-default:
	$(PYTHON) -m quant_scripts.spx_gex --mode fetch-spy-bars --dataset $(DATASET) --symbol $(SYMBOL) --start $${START:-$(DEFAULT_START)} --end $${END:-$(DEFAULT_END)} --output $(OUTPUT)

backtest:
	$(PYTHON) -m quant_scripts.spx_gex --mode backtest --point $(POINT) --bars $(BARS) --output $(OUTPUT)

walk-forward:
	$(PYTHON) -m quant_scripts.spx_gex --mode walk-forward --input $(INPUT) --output $(OUTPUT)

test:
	$(PYTHON) -m unittest discover -s $(TEST_DIR) -q
