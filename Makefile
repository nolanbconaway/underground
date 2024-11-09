.PHONY:
lint:
	@ ruff check
	@ ruff format --check

.PHONY:
format:
	@ ruff check --select I --fix
	@ ruff format

.PHONY:
pytest:
	pytest test --verbose

.PHONY:
lint-test: lint pytest
