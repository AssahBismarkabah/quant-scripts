.PHONY: help harvest harvest-free

VENV := $(CURDIR)/../../.venv
PY := $(VENV)/bin/python
SCRIPT := $(CURDIR)/harvest_frontier.py

help:
	@printf '%s\n' \
		'Research frontier mining (find the next testable candidate):' \
		'  make harvest         full harvest (arXiv + OpenAlex/SSRN + Crossref + Scholar + SSRN/ZenRows)' \
		'  make harvest-free    harvest without the credit-consuming ZenRows-SSRN source'

harvest:
	$(PY) $(SCRIPT) \
		--max-arxiv 200 --openalex-pages 1 --crossref-rows 50 \
		--scholar-results 30 --zenrows-results 100

harvest-free:
	$(PY) $(SCRIPT) \
		--max-arxiv 200 --openalex-pages 1 --crossref-rows 50 \
		--scholar-results 30 --sources arxiv,openalex,crossref,scholar
