help:
	@echo "lint - check style with flake8"
	@echo "test - run tests against current environment"
	@echo "test-all - run tests using tox"
	@echo "install"

lint:
	flake8 .

test:
	pytest

test-all:
	tox

install:
	pip install .

install-dev:
	pip install -r requirements.txt
	pip install -e .
