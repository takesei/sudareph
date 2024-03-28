.PHONY: all, check, format, typing, test

all: format check typing test init

check:
	@poetry run ruff check

format:
	@poetry run ruff format

typing:
	@poetry run mypy

test:
	@poetry run pytest -v -s --pdb --ff --doctest-modules

init:
	@poetry install
	@pre-commit install
