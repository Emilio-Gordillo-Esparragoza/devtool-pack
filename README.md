# DevToolPack

A modular CLI tool for installing DevOps tools (Terraform, AWS CLI, kubectl) across multiple shells.

## Features

- Install DevOps tools with a simple command: `devpack install <tool>`
- Check installation status: `devpack doctor`
- List available tools: `devpack list-tools`
- Automatic PATH configuration for bash, zsh, fish, cmd, and PowerShell
- Cross-platform support (Windows, Linux, macOS)
- Lazy imports for faster startup
- Modular design for easy extension

## Installation

```bash
pip install -e .
```

## Usage

### List available tools
```bash
devpack list-tools
```

### Install a tool
```bash
devpack install terraform
devpack install awscli
devpack install kubectl
```

### Check installation status
```bash
devpack doctor
```

## Supported Tools

- Terraform
- AWS CLI
- Kubectl

## Architecture

DevToolPack follows a modular architecture:

- `cli.py`: Main CLI entry point using Typer
- `commands/`: Individual command implementations (install, doctor, list)
- `tools/`: Tool-specific implementations (terraform.py, awscli.py, kubectl.py)
- `installer/`: Download and extraction logic
- `env/`: Environment management (PATH handling, shell detection)
- `utils/`: Utility functions (logging, system checks)
- `doctor/`: Validation logic

## Development

### Running Tests
```bash
pytest -v
```

### Linting
```bash
ruff check .
```

### Building
```bash
pip install -e .[dev]
```

## License

MIT
