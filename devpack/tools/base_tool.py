from abc import ABC, abstractmethod
import os
import platform
from pathlib import Path
from typing import Optional, Dict

import yaml

from devpack.env.package_manager import get_package_manager


def _load_tools_config() -> dict:
    """Load tools.yaml from the configs directory.

    Checks multiple locations:
    1. Repo root (development): ../../../configs/tools.yaml
    2. Package install (devpack/configs): ../../configs/tools.yaml
    3. Package install (root configs): ../../../configs/tools.yaml (from hatch include)
    """
    base = Path(__file__).parent
    candidates = [
        base.parent.parent.parent / "configs" / "tools.yaml",  # repo root (dev)
        base.parent.parent / "configs" / "tools.yaml",  # devpack/configs (installed)
        base.parent.parent.parent
        / "configs"
        / "tools.yaml",  # root configs (installed via hatch)
    ]
    for config_path in candidates:
        if config_path.exists():
            with config_path.open() as f:
                return yaml.safe_load(f) or {}
    return {}


def _current_os() -> str:
    """Return a normalised OS token: windows | linux | darwin."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    if system == "darwin":
        return "darwin"
    return "linux"


def _current_arch() -> str:
    """Return a normalised arch token: amd64 | arm64."""
    machine = platform.machine().lower()
    if machine in ("arm64", "aarch64"):
        return "arm64"
    return "amd64"


class BaseTool(ABC):
    """Abstract base class for all tools."""

    #: Key used to look up this tool in configs/tools.yaml.
    #: Subclasses may override; defaults to ``self.name``.
    config_key: Optional[str] = None

    #: Mapping of package manager to package name.
    #: e.g., {"apt": "terraform", "pacman": "terraform", "brew": "terraform"}
    package_names: Dict[str, str] = {}

    def __init__(self, name: str):
        self.name = name
        self.bin_dir = Path.home() / ".devpack" / "bin"
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        self._pm = get_package_manager()

    @property
    def binary_name(self) -> str:
        """Binary filename, with .exe suffix on Windows."""
        if os.name == "nt":
            return f"{self.name}.exe"
        return self.name

    def _resolve_url(self) -> str:
        """Return the download URL for the current OS/arch from tools.yaml.

        Lookup order for each tool section:
        1. ``<os>_<arch>_url``   (e.g. ``linux_amd64_url``)
        2. ``<os>_url``          (e.g. ``windows_url``)
        3. ``url``               (generic fallback)

        Returns an empty string when no matching key is found.
        """
        key = self.config_key or self.name
        config = _load_tools_config().get(key, {})
        cur_os = _current_os()
        cur_arch = _current_arch()

        for candidate in (
            f"{cur_os}_{cur_arch}_url",
            f"{cur_os}_url",
            "url",
        ):
            if candidate in config:
                return config[candidate]
        return ""

    @property
    @abstractmethod
    def download_url(self) -> str:
        """URL to download the tool binary."""
        pass

    @abstractmethod
    def install(self) -> None:
        """Download and install the tool."""
        pass

    def get_binary_path(self) -> Path:
        """Full path to the installed binary."""
        return self.bin_dir / self.binary_name

    def _install_via_package_manager(self) -> bool:
        """Try to install the tool via system package manager.

        Returns:
            True if installation succeeded, False otherwise.
        """
        if not self.package_names:
            return False

        print(
            f"Attempting to install {self.name} via system package manager ({self._pm.detect()})..."
        )
        success = self._pm.install(
            [self.name], {self.name: self.package_names}
        )
        if success:
            print(f"{self.name} installed successfully via package manager.")
        return success

    def _is_installed_via_package_manager(self) -> bool:
        """Check if tool is installed via package manager."""
        if not self.package_names:
            return False
        return self._pm.is_installed(
            self.name, {self.name: self.package_names}
        )

    def is_installed(self) -> bool:
        """Check if the tool binary exists in the bin directory or via package manager."""
        if self._is_installed_via_package_manager():
            return True
        binary_path = self.get_binary_path()
        return binary_path.is_file() and os.access(binary_path, os.X_OK)
