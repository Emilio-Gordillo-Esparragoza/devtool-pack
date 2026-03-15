name: lint
description: Linting and formatting

1. `ruff check . --fix`
2. `ruff format .`
3. `pytest -q` (verify tests still pass)
4. Commit: `style: apply ruff fixes`