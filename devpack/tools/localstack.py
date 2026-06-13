import sys
import subprocess
import shutil
from pathlib import Path
from devpack.tools.base_tool import BaseTool
from devpack.env.path_manager import add_to_path


class LocalStackTool(BaseTool):
    """LocalStack tool installer (pip package)."""

    def __init__(self):
        super().__init__("localstack")

    @property
    def download_url(self) -> str:
        return ""

    def is_installed(self) -> bool:
        return shutil.which("localstack") is not None

    def get_binary_path(self):
        path = shutil.which("localstack")
        return Path(path) if path else self.bin_dir / self.binary_name

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
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
