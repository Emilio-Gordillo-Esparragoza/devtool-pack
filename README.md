# DevToolPack

> One command to set up your entire DevOps environment — on any machine, any OS, any shell.

[![CI](https://github.com/Emilio-Gordillo-Esparragoza/devtool-pack/actions/workflows/ci.yml/badge.svg)](https://github.com/Emilio-Gordillo-Esparragoza/devtool-pack/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

---

## The problem it solves

You join a new project. The README says *"install Terraform, kubectl, AWS CLI, and Docker before you start."* You spend the next hour hunting download pages, unzipping archives, figuring out why `terraform` isn't on your PATH, and wondering why the version you grabbed is different from what CI uses.

DevToolPack removes that friction. One CLI, one command per tool, automatic PATH wiring — and it works the same way on Windows, macOS, and Linux (including Arch-based distros like CachyOS).

---

## How much time does it actually save?

Manual environment setup for a typical DevOps stack takes **45–90 minutes** on a fresh machine:

| Task | Manual | DevToolPack |
|---|---|---|
| Install Terraform | ~10 min | `devpack install terraform` |
| Install kubectl | ~8 min | `devpack install kubectl` |
| Install AWS CLI | ~12 min | `devpack install awscli` |
| Install Go | ~10 min | `devpack install golang` |
| Install Rust | ~8 min | `devpack install rust` |
| Configure PATH for all tools | ~15 min | automatic |
| Verify everything works | ~10 min | `devpack doctor` |
| **Total** | **~73 min** | **< 5 min** |

That's not just onboarding time. It's every time you provision a CI runner, spin up a dev container, or set up a new machine.

---

## Quick start

```bash
pip install devtoolpack
```

Install a tool:

```bash
devpack install terraform
devpack install kubectl
devpack install golang
```

Check your environment:

```bash
devpack doctor
```

List everything available:

```bash
devpack list-tools
```

---

## Supported tools

| Tool | Method | Windows | Linux | macOS |
|---|---|---|---|---|
| Terraform | Binary | ✅ | ✅ | ✅ |
| AWS CLI | Binary/MSI | ✅ | ✅ | ✅ |
| kubectl | Binary | ✅ | ✅ | ✅ |
| Git | Binary/pkg manager | ✅ | ✅ | ✅ |
| AWS SAM CLI | Binary | ✅ | ✅ | ✅ |
| LocalStack | pip | ✅ | ✅ | ✅ |
| AWS CDK | npm | ✅ | ✅ | ✅ |
| Docker | Installer/script | ✅ | ✅ | — |
| Rust | rustup | ✅ | ✅ | ✅ |
| Go | Binary | ✅ | ✅ | ✅ |

Linux package manager support: `apt`, `pacman` (Arch/CachyOS/Manjaro), `dnf`, `yum`, `zypper`.

> Docker on macOS requires manual installation via [Docker Desktop](https://docs.docker.com/desktop/install/mac-install/).

---

## Shell support

DevToolPack writes PATH entries to the right config file automatically:

| Shell | Config file |
|---|---|
| bash | `~/.bashrc` |
| zsh | `~/.zshrc` |
| fish | `~/.config/fish/config.fish` |
| PowerShell | `Microsoft.PowerShell_profile.ps1` |
| cmd.exe | Windows registry (`HKCU\Environment`) |

Changes take effect in the current session immediately (no restart needed) and persist across new sessions.

---

## Automate with a hook

If your team uses Kiro, you can wire DevToolPack into a `postTaskExecution` hook so every new environment is validated automatically after setup tasks complete:

```json
{
  "name": "Verify DevOps environment",
  "version": "1.0.0",
  "description": "Run devpack doctor after any setup task completes",
  "when": {
    "type": "postTaskExecution"
  },
  "then": {
    "type": "runCommand",
    "command": "devpack doctor"
  }
}
```

Save this as `.kiro/hooks/verify-env.json` and `devpack doctor` will run automatically after each task — catching missing tools before they block anyone.

---

## Project structure

```
devpack/
├── cli.py              # Typer entry point
├── commands/           # install, doctor, list-tools
├── tools/              # One file per tool (terraform.py, kubectl.py, …)
├── installer/          # Download + extraction engine
├── env/                # PATH management, shell detection
├── doctor/             # Installation validator
└── utils/              # Logger

configs/
└── tools.yaml          # Versions and download URLs per OS/arch
```

Tool configuration lives in `configs/tools.yaml`. URL resolution follows the pattern `<os>_<arch>_url` → `<os>_url` → `url`, so adding arm64 support for a new tool is a one-line YAML change.

---

## Development

```bash
git clone https://github.com/Emilio-Gordillo-Esparragoza/devtool-pack.git
cd devtool-pack
pip install -e ".[dev]"
```

Run tests:

```bash
pytest -q
```

Run tests with coverage:

```bash
pytest --cov=devpack --cov-report=term-missing
```

Lint:

```bash
ruff check devpack tests
```

Add a new tool: see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
