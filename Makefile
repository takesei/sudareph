.PHONY: all, check, format, typing, test

all: format check typing test

check:
	@poetry run ruff check --fix

format:
	@poetry run ruff format

typing:
	@poetry run mypy

test:
	@poetry run pytest -v -s --ff --doctest-modules --cov=sudareph --cov-report=term

itest:
	@poetry run pytest -v -s --pdb --ff --doctest-modules --cov=sudareph --cov-report=term

init:
	@poetry install
	@pre-commit install
