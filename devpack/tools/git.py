import os
import subprocess
import shutil
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.env.path_manager import add_to_path


class GitTool(BaseTool):
    """Git tool installer."""

    config_key = "git"

    def __init__(self):
        super().__init__("git")

    @property
    def download_url(self) -> str:
        return self._resolve_url()

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        if shutil.which("git"):
            print(f"{self.name} is already available in the system PATH.")
            return

        if os.name == "nt":
            self._install_windows()
        else:
            self._install_unix()

    def _install_windows(self) -> None:  # pragma: no cover
        url = self.download_url
        if not url:
            raise RuntimeError("No download URL found for Git on Windows.")
        print(f"Downloading {self.name}...")
        installer_path = download_file(url, self.bin_dir)
        print(f"Running {self.name} installer...")
        subprocess.run([str(installer_path), "-o", str(self.bin_dir), "-y"], check=True)
        git_exe = self.bin_dir / "bin" / "git.exe"
        add_to_path(str(git_exe.parent if git_exe.exists() else self.bin_dir))
        print(f"{self.name} installed successfully.")

    def _install_unix(self) -> None:
        """Install Git on Linux via the system package manager."""
        import platform
        system = platform.system().lower()
        if system == "darwin":
            subprocess.run(["brew", "install", "git"], check=True)
        else:
            if shutil.which("apt-get"):
                subprocess.run(["sudo", "apt-get", "install", "-y", "git"], check=True)
            elif shutil.which("pacman"):
                subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "git"], check=True)
            elif shutil.which("dnf"):
                subprocess.run(["sudo", "dnf", "install", "-y", "git"], check=True)
            elif shutil.which("yum"):
                subprocess.run(["sudo", "yum", "install", "-y", "git"], check=True)
            elif shutil.which("zypper"):
                subprocess.run(["sudo", "zypper", "install", "-y", "git"], check=True)
            else:
                raise RuntimeError(
                    "Unsupported Linux package manager. Install git manually."
                )
        add_to_path(str(self.bin_dir))
        print(f"{self.name} installed successfully.")
