import os
import subprocess
import shutil
from pathlib import Path
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.env.path_manager import add_to_path


class DockerTool(BaseTool):
    """Docker tool installer."""

    def __init__(self):
        super().__init__("docker")

    @property
    def download_url(self) -> str:
        return "https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe"

    def is_installed(self) -> bool:
        return shutil.which("docker") is not None

    def get_binary_path(self):
        path = shutil.which("docker")
        return Path(path) if path else self.bin_dir / self.binary_name

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        if os.name == "nt":
            print(f"Downloading {self.name} Desktop installer...")
            installer_path = download_file(self.download_url, self.bin_dir)
            print(f"Running {self.name} Desktop installer...")
            subprocess.run([str(installer_path), "install", "--quiet"], check=True)
            docker_bin = shutil.which("docker")
            if docker_bin:
                add_to_path(str(Path(docker_bin).parent))
            print(f"{self.name} installed successfully.")
        else:
            print(
                f"{self.name} installation on {os.name} is not supported via devtoolpack. "
                "Please install Docker manually."
            )
