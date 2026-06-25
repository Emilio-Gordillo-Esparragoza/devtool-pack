import os
import subprocess
import shutil
from pathlib import Path
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.env.path_manager import add_to_path


class DockerTool(BaseTool):
    """Docker tool installer."""

    config_key = "docker"

    package_names = {
        "apt": "docker.io",
        "pacman": "docker",
        "dnf": "docker",
        "yum": "docker",
        "brew": "docker",
        "choco": "docker-desktop",
        "winget": "Docker.DockerDesktop",
    }

    def __init__(self):
        super().__init__("docker")

    @property
    def download_url(self) -> str:
        return self._resolve_url()

    def is_installed(self) -> bool:
        return (
            shutil.which("docker") is not None
            or self._is_installed_via_package_manager()
        )

    def get_binary_path(self) -> Path:
        path = shutil.which("docker")
        return Path(path) if path else self.bin_dir / self.binary_name

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        if self._install_via_package_manager():
            self._post_install()
            return

        if os.name == "nt":
            self._install_windows()
        else:
            self._install_unix()

    def _install_windows(self) -> None:  # pragma: no cover
        url = self.download_url
        if not url:
            raise RuntimeError("No download URL found for Docker on Windows.")
        print(f"Downloading {self.name} Desktop installer...")
        installer_path = download_file(url, self.bin_dir)
        print(f"Running {self.name} Desktop installer (this may take a while)...")
        subprocess.run([str(installer_path), "install", "--quiet"], check=True)
        self._post_install()

    def _install_unix(self) -> None:
        """Install Docker Engine on Linux."""
        import platform

        if platform.system().lower() == "darwin":
            raise RuntimeError(
                "Docker Desktop for macOS must be installed manually: "
                "https://docs.docker.com/desktop/install/mac-install/"
            )

        if self._pm.is_arch_based():
            print("Detected Arch-based distribution. Installing Docker via pacman...")
            subprocess.run(
                ["sudo", "pacman", "-Sy", "--noconfirm", "docker"],
                check=True,
            )
            print("Enabling and starting Docker service...")
            subprocess.run(
                ["sudo", "systemctl", "enable", "--now", "docker"],
                check=True,
            )
        else:
            print("Installing Docker Engine via convenience script...")
            subprocess.run(
                ["sh", "-c", "curl -fsSL https://get.docker.com | sh"],
                check=True,
            )
        self._post_install()

    def _post_install(self) -> None:
        docker_bin = shutil.which("docker")
        if docker_bin:
            add_to_path(str(Path(docker_bin).parent))
        print(f"{self.name} installed successfully.")
