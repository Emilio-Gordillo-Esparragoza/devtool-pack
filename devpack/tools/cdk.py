import subprocess
import shutil
from pathlib import Path
from devpack.tools.base_tool import BaseTool
from devpack.env.path_manager import add_to_path


class CDKTool(BaseTool):
    """AWS CDK tool installer (npm package)."""

    def __init__(self):
        super().__init__("cdk")

    @property
    def download_url(self) -> str:
        return ""

    def is_installed(self) -> bool:
        return shutil.which("cdk") is not None

    def get_binary_path(self):
        path = shutil.which("cdk")
        return Path(path) if path else self.bin_dir / self.binary_name

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        npm = shutil.which("npm")
        if not npm:
            print("npm is required to install AWS CDK. Please install Node.js first.")
            raise RuntimeError("npm not found")

        print(f"Installing {self.name} via npm...")
        subprocess.run([npm, "install", "-g", "aws-cdk"], check=True)
        cdk_bin = shutil.which("cdk")
        if cdk_bin:
            add_to_path(str(Path(cdk_bin).parent))
        print(f"{self.name} installed successfully.")
