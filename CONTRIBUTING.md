# Contributing to DevToolPack

Thanks for taking the time to contribute. This guide covers everything you need to add a new tool, fix a bug, or improve the project.

---

## Getting started

```bash
git clone https://github.com/Emilio-Gordillo-Esparragoza/devtool-pack.git
cd devtool-pack
pip install -e ".[dev]"
```

Verify the setup:

```bash
pytest -q          # all tests should pass
ruff check devpack tests   # no lint errors
```

---

## Adding a new tool

The project uses a skill for this. The full pattern is:

### 1. Add the tool config to `configs/tools.yaml`

```yaml
mytool:
  name: mytool
  version: "1.0.0"
  windows_amd64_url: "https://example.com/mytool-1.0.0-windows-amd64.zip"
  linux_amd64_url:   "https://example.com/mytool-1.0.0-linux-amd64.tar.gz"
  linux_arm64_url:   "https://example.com/mytool-1.0.0-linux-arm64.tar.gz"
  darwin_amd64_url:  "https://example.com/mytool-1.0.0-darwin-amd64.tar.gz"
  darwin_arm64_url:  "https://example.com/mytool-1.0.0-darwin-arm64.tar.gz"
```

URL keys follow the pattern `<os>_<arch>_url` → `<os>_url` → `url`. You only need the keys that exist — the resolver tries the most specific first.

### 2. Create `devpack/tools/mytool.py`

Use this as your base:

```python
import os
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.installer.extractor import extract_archive
from devpack.env.path_manager import add_to_path


class MytoolTool(BaseTool):
    """Mytool installer."""

    config_key = "mytool"

    def __init__(self):
        super().__init__("mytool")

    @property
    def download_url(self) -> str:
        return self._resolve_url()

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        url = self.download_url
        if not url:
            raise RuntimeError(f"No download URL found for {self.name} on this platform.")

        print(f"Downloading {self.name}...")
        archive_path = download_file(url, self.bin_dir)

        print(f"Extracting {self.name}...")
        extracted_path = extract_archive(archive_path, self.bin_dir)

        binary_name = "mytool.exe" if os.name == "nt" else "mytool"
        binary_path = extracted_path / binary_name
        if not binary_path.exists():
            binary_path = self.bin_dir / binary_name

        if os.name != "nt":
            os.chmod(binary_path, 0o755)

        if binary_path.parent != self.bin_dir:
            binary_path.rename(self.bin_dir / binary_name)

        archive_path.unlink()
        add_to_path(str(self.bin_dir))
        print(f"{self.name} installed successfully.")
```

If the tool installs via pip or npm instead of a binary, follow the pattern in `localstack.py` or `cdk.py`.

### 3. Register the tool in the CLI

In `devpack/commands/install.py`, add the import and entry:

```python
from devpack.tools.mytool import MytoolTool

# inside tool_map:
"mytool": MytoolTool(),
```

Do the same in `devpack/commands/list_.py` (add the name to the list) and `devpack/doctor/validator.py` (add a tuple to the `tools` list).

### 4. Write tests

Create `tests/test_mytool.py`. At minimum cover:

- initialization (`name`, `bin_dir`)
- `download_url` for each platform (mock `_current_os` / `_current_arch`)
- `install()` happy path (mock `download_file`, `extract_archive`, `add_to_path`)
- `install()` when already installed
- `install()` when no URL is found (expect `RuntimeError`)

### 5. Run and verify

```bash
pytest -q
ruff check devpack tests
pytest --cov=devpack --cov-fail-under=85
```

### 6. Commit

```
feat: add <toolname> tool
```

---

## Bug fixes

1. Open an issue describing the bug and the expected behaviour before starting work on non-trivial fixes.
2. Write a failing test that reproduces the bug first.
3. Fix the code until the test passes.
4. Commit: `fix: <short description>`

---

## Code style

- Type hints on all public functions.
- PEP 8, 88 chars/line — enforced by `ruff`.
- `snake_case` everywhere.
- One responsibility per module (SRP).
- Lazy imports inside methods when the import is only needed for one code path (see `git.py` for an example).

---

## Pull requests

- Branch off `main`, push to a feature branch.
- Keep PRs focused — one logical change per PR.
- CI must be green before requesting review (lint + tests + 85% coverage).
- PR title follows conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`.

---

## Project layout quick reference

```
devpack/tools/      ← add new tool here
configs/tools.yaml  ← add download URLs here
tests/              ← add test_<toolname>.py here
devpack/commands/   ← register the tool in install.py and list_.py
devpack/doctor/     ← register the tool in validator.py
```
