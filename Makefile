.PHONY:
lint:
	@ ruff check
	@ ruff format --check

.PHONY:
format:
	@ ruff check --select I --fix
	@ ruff format

.PHONY:
test:
	@ pytest tests --verbose

.PHONY:
lint-test: lint test
