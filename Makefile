PYTHON ?= python3
FILE ?= examples/prog1.lcc

.PHONY: run test clean

run:
	$(PYTHON) -m src.main $(FILE)

test:
	$(PYTHON) -m unittest discover -s tests

clean:
	rm -rf __pycache__ src/__pycache__ tests/__pycache__ .pytest_cache
