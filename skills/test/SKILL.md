name: test
description: Run full test suite

1. `pytest -q`
2. If fails, show errors and stop
3. If passes: `pytest --cov=devpack --cov-report=terminal`
4. Report minimum 85% coverage