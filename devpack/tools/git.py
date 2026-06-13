import os
import subprocess
import shutil
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.env.path_manager import add_to_path


class GitTool(BaseTool):
    """Git tool installer."""

    def __init__(self):
        super().__init__("git")

    @property
    def download_url(self) -> str:
        return (
            "https://github.com/git-for-windows/git/releases/download/v2.41.0.windows.3/"
            "PortableGit-2.41.0.3-64-bit.7z.exe"
        )

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        if shutil.which("git"):
            print(f"{self.name} is already available in the system PATH.")
            return

        print(f"Downloading {self.name}...")
        installer_path = download_file(self.download_url, self.bin_dir)

        if os.name == "nt":
            print(f"Running {self.name} installer...")
            subprocess.run(
                [str(installer_path), "-o", str(self.bin_dir), "-y"], check=True
            )
            git_exe = self.bin_dir / "bin" / "git.exe"
            if git_exe.exists():
                add_to_path(str(git_exe.parent))
            else:
                add_to_path(str(self.bin_dir))
            print(f"{self.name} installed successfully.")
        else:
            print(f"{self.name} installation on {os.name} not implemented.")
