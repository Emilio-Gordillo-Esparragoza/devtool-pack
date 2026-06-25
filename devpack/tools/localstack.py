import sys
import subprocess
import shutil
from pathlib import Path
from devpack.tools.base_tool import BaseTool
from devpack.env.path_manager import add_to_path


class LocalStackTool(BaseTool):
    """LocalStack tool installer (pip package)."""

    package_names = {
        "apt": "localstack",
        "pacman": "localstack",
        "dnf": "localstack",
        "yum": "localstack",
        "brew": "localstack",
        "choco": "localstack",
        "winget": "LocalStack.LocalStack",
    }

    def __init__(self):
        super().__init__("localstack")

    @property
    def download_url(self) -> str:
        return ""

    def is_installed(self) -> bool:
        return (
            shutil.which("localstack") is not None
            or self._is_installed_via_package_manager()
        )

    def get_binary_path(self):
        path = shutil.which("localstack")
        return Path(path) if path else self.bin_dir / self.binary_name

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        if self._install_via_package_manager():
            print(f"{self.name} installed successfully.")
            return

        print(f"Installing {self.name} via pip...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "localstack"],
            check=True,
        )
        localstack_bin = shutil.which("localstack")
        if localstack_bin:
            add_to_path(str(Path(localstack_bin).parent))
        print(f"{self.name} installed successfully.")
