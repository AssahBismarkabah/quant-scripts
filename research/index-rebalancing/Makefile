PYTHON ?= ../../.venv/bin/python
ifneq ($(wildcard ../../.venv/bin/python),)
PYTHON := ../../.venv/bin/python
else ifneq ($(wildcard ./.venv/bin/python),)
PYTHON := ./.venv/bin/python
else
PYTHON ?= python3
endif
export PYTHONPATH := ../../src:$(PYTHONPATH)

TEST_DIR ?= ../../tests
MIN_ANN ?= 2022-06-01
VENUE ?=
LIMIT ?=
STRESS ?=

.PHONY: help sweep parse cross reconcile ftse r2000 bars study s10 level2 all test

help:
	@printf '%s\n' \
		'Index rebalancing research workflow (Level 1):' \
		'  make sweep            sweep S&P DJI press archive pages' \
		'  make parse            download + parse release pages into parsed_releases.jsonl' \
		'  make cross            fetch Wikipedia + tickerleague change tables' \
		'  make reconcile        build spdji event table + cross-source reconcile (GATE 4)' \
		'  make ftse             download FTSE Russell lists (live + Wayback)' \
		'  make r2000            parse Russell PDFs, derive R2000 events, validate counts' \
		'  make bars             fetch daily bars + benchmark ETFs + calendar (needs Databento key)' \
		'  make study            run event study (base + stress) and write aggregates' \
		'  make s10              bootstrap + Monte Carlo validation of study cells (S10)' \
		'  make level2           L2 robustness: liquidity sweep, years, capacity, borrow' \
		'  make all              sweep -> parse -> cross -> reconcile -> ftse -> r2000' \
		'  make test             run unit tests'

sweep:
	$(PYTHON) -m quant_scripts.index_rebalancing --mode sweep-spdji

parse:
	$(PYTHON) -m quant_scripts.index_rebalancing --mode parse-releases --min-announcement $(MIN_ANN) $(if $(LIMIT),--limit $(LIMIT))

cross:
	$(PYTHON) -m quant_scripts.index_rebalancing --mode fetch-wikipedia $(if $(VENUE),--venue $(VENUE))
	$(PYTHON) -m quant_scripts.index_rebalancing --mode fetch-tickerleague $(if $(VENUE),--venue $(VENUE))

reconcile:
	$(PYTHON) -m quant_scripts.index_rebalancing --mode reconcile --min-announcement $(MIN_ANN)

ftse:
	$(PYTHON) -m quant_scripts.index_rebalancing --mode fetch-ftse

r2000:
	$(PYTHON) -m quant_scripts.index_rebalancing --mode derive-r2000

bars:
	$(PYTHON) -m quant_scripts.index_rebalancing --mode fetch-bars $(if $(LIMIT),--limit $(LIMIT))

study:
	$(PYTHON) -m quant_scripts.index_rebalancing --mode run-study
	$(PYTHON) -m quant_scripts.index_rebalancing --mode run-study --stress

s10:
	$(PYTHON) -m quant_scripts.index_rebalancing --mode validate-s10

level2:
	$(PYTHON) -m quant_scripts.index_rebalancing --mode level2-analysis

all: sweep parse cross reconcile ftse r2000

test:
	$(PYTHON) -m pytest $(TEST_DIR)/test_index_rebalancing.py -q
