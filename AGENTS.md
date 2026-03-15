# AGENTS.md – devtoolpack

## Objective
Develop devtoolpack: modular CLI for installing DevOps tools (Terraform, AWS CLI, kubectl) across multiple shells.

## Code Style
- Type hints in public functions
- PEP 8, 88 chars/line (ruff applies)
- snake_case, SRP per command
- Lazy imports per command

## Typical Flow
1. Read relevant module with `cat`
2. Execute `pytest -q`
3. Update README/docstrings
4. Conventional commit: `feat: add tool`, `fix: path resolution`

## Useful Commands
/run tests
/run lint
/skill add-tool
/skill test

## Permissions
edit: allow
bash: allow
webfetch: ask