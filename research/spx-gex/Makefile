PYTHON ?= ../../.venv/bin/python
ifneq ($(wildcard ../../.venv/bin/python),)
PYTHON := ../../.venv/bin/python
else ifneq ($(wildcard ./.venv/bin/python),)
PYTHON := ./.venv/bin/python
else
PYTHON ?= python3
endif
export PYTHONPATH := ../../src:$(PYTHONPATH)

DEFAULT_START ?= 2023-04-03T00:00:00+00:00
DEFAULT_END ?= 2023-04-04T00:00:00+00:00
TEST_DIR ?= ../../tests
DATASET ?= EQUS.MINI
SYMBOL ?= SPY
START ?=
END ?=
DATA_DIR ?= data
DEFAULT_BARS := $(DATA_DIR)/spy_bars.json
DEFAULT_POINT := $(DATA_DIR)/spx_point.json
DEFAULT_MERGED_POINT := $(DATA_DIR)/spx_point_merged.json
DEFAULT_OI := $(DATA_DIR)/spx_open_interest.csv
RAW_POINT := $(DATA_DIR)/raw/cboe_spx.csv
OUTPUT ?= $(DEFAULT_BARS)
BACKTEST_OUTPUT ?= $(DATA_DIR)/backtest_report.json
POINT ?= $(DEFAULT_POINT)
BARS ?= $(DEFAULT_BARS)
INPUT ?= $(RAW_POINT)
CHAIN ?=
OI ?=
MERGED_POINT ?= $(DEFAULT_MERGED_POINT)
OI_OUTPUT ?= $(DEFAULT_OI)

.DEFAULT_GOAL := backtest-merged-default

.PHONY: help test smoke template backtest walk-forward point-template bars-template sessions-template csv-template normalize-cboe normalize-optionsdx fetch-databento-oi fetch-spy-bars backtest-default prepare prepare-point prepare-bars prepare-merged backtest-merged

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
		'  make normalize-optionsdx INPUT=...' \
		'  make prepare-point INPUT=...' \
		'  make fetch-databento-oi START=... END=... OUTPUT=...' \
		'  make prepare-merged CHAIN=... OI=...' \
		'  make fetch-spy-bars START=... END=... OUTPUT=...' \
		'  make prepare' \
		'  make backtest-merged CHAIN=... OI=...' \
		'  make backtest' \
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

normalize-optionsdx:
	$(PYTHON) -m quant_scripts.spx_gex --mode normalize-optionsdx --input $(INPUT)

fetch-databento-oi:
	$(PYTHON) -m quant_scripts.spx_gex --mode fetch-databento-oi --oi-dataset $(if $(OI_DATASET),$(OI_DATASET),OPRA.PILLAR) --oi-symbol $(if $(OI_SYMBOL),$(OI_SYMBOL),SPX.OPT) --oi-schema $(if $(OI_SCHEMA),$(OI_SCHEMA),statistics) --start $(if $(START),$(START),$(DEFAULT_START)) --end $(if $(END),$(END),$(DEFAULT_END)) --output $(OI_OUTPUT)

prepare-point:
	@mkdir -p $(DATA_DIR)
	@test -f $(INPUT) || (printf '%s\n' "missing raw SPX export: $(INPUT)" && exit 1)
	$(PYTHON) -m quant_scripts.spx_gex --mode normalize-cboe --input $(INPUT) > $(DEFAULT_POINT)

prepare-merged:
	@mkdir -p $(DATA_DIR)
	@test -n "$(CHAIN)" || (printf '%s\n' "missing CHAIN=..." && exit 1)
	@test -n "$(OI)" || (printf '%s\n' "missing OI=..." && exit 1)
	@test -f $(CHAIN) || (printf '%s\n' "missing chain input: $(CHAIN)" && exit 1)
	@test -f $(OI) || (printf '%s\n' "missing oi input: $(OI)" && exit 1)
	$(PYTHON) -m quant_scripts.spx_gex --mode merge-optionsdx-oi --chain $(CHAIN) --oi $(OI) --output $(MERGED_POINT)

fetch-spy-bars:
	$(PYTHON) -m quant_scripts.spx_gex --mode fetch-spy-bars --dataset $(DATASET) --symbol $(SYMBOL) --start $(if $(START),$(START),$(DEFAULT_START)) --end $(if $(END),$(END),$(DEFAULT_END)) --output $(OUTPUT)

backtest:
	$(PYTHON) -m quant_scripts.spx_gex --mode backtest --point $(POINT) --bars $(BARS) --output $(BACKTEST_OUTPUT)

backtest-default: prepare
	$(PYTHON) -m quant_scripts.spx_gex --mode backtest --point $(DEFAULT_POINT) --bars $(DEFAULT_BARS) --output $(BACKTEST_OUTPUT)

backtest-merged: prepare-merged
	$(PYTHON) -m quant_scripts.spx_gex --mode backtest --point $(MERGED_POINT) --bars $(DEFAULT_BARS) --output $(BACKTEST_OUTPUT)

backtest-merged-default:
	@test -s $(OI_OUTPUT) || $(MAKE) fetch-databento-oi
	@test -s $(DEFAULT_BARS) || $(MAKE) fetch-spy-bars START=2023-04-03T13:30:00+00:00 END=2023-04-03T20:00:00+00:00 OUTPUT=$(DEFAULT_BARS)
	$(MAKE) backtest-merged CHAIN=../../spx_eod_extract/spx_eod_2023q2-kdxt36/spx_eod_202304.txt OI=$(OI_OUTPUT)

prepare:
	@mkdir -p $(DATA_DIR)
	$(MAKE) prepare-point INPUT=$(INPUT)
	$(MAKE) fetch-databento-oi
	$(MAKE) prepare-bars

prepare-bars:
	$(PYTHON) -m quant_scripts.spx_gex --mode fetch-spy-bars --dataset $(DATASET) --symbol $(SYMBOL) --start $${START:-$(DEFAULT_START)} --end $${END:-$(DEFAULT_END)} --output $(DEFAULT_BARS)

walk-forward:
	$(PYTHON) -m quant_scripts.spx_gex --mode walk-forward --input $(INPUT) --output $(OUTPUT)

test:
	$(PYTHON) -m unittest discover -s $(TEST_DIR) -q
