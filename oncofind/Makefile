.PHONY: install install-dev test coverage lint format clean build

install:
	pip install -e .

install-dev:
	pip install -e .[dev]

test:
	pytest

coverage:
	pytest --cov=oncofind --cov-report=term-missing --cov-report=html

lint:
	ruff check .
	mypy oncofind --strict --ignore-missing-imports

format:
	ruff format .

build:
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
