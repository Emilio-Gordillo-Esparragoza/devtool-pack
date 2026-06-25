import os
import subprocess
import shutil
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.env.path_manager import add_to_path


class AWSCLITool(BaseTool):
    """AWS CLI tool installer."""

    config_key = "awscli"

    package_names = {
        "apt": "awscli",
        "pacman": "aws-cli-v2",
        "dnf": "awscli2",
        "yum": "awscli2",
        "brew": "awscli",
        "choco": "awscli",
        "winget": "Amazon.AWSCLI",
    }

    def __init__(self):
        super().__init__("aws")

    @property
    def download_url(self) -> str:
        return self._resolve_url()

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        if self._install_via_package_manager():
            print(f"{self.name} installed successfully.")
            return

        url = self.download_url
        if not url:
            raise RuntimeError("No download URL found for AWS CLI on this platform.")

        print(f"Downloading {self.name}...")

        if os.name == "nt":
            self._install_windows(url)
        else:
            self._install_unix(url)

    def _install_windows(self, url: str) -> None:  # pragma: no cover
        msi_path = download_file(url, self.bin_dir)
        install_dir = self.bin_dir / "aws-cli"
        install_dir.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                ["msiexec", "/i", str(msi_path), "/qn", f"TARGETDIR={install_dir}"],
                check=True,
                capture_output=True,
            )
            aws_bin_dir = install_dir / "aws" / "bin"
            if aws_bin_dir.is_dir():
                add_to_path(str(aws_bin_dir))
            else:
                add_to_path(str(install_dir))
            print(f"{self.name} installed successfully.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"MSI installation failed: {e}") from e
        finally:
            try:
                msi_path.unlink()
            except OSError:
                pass

    def _install_unix(self, url: str) -> None:
        """Install AWS CLI v2 on Linux/macOS via the bundled zip installer."""
        import zipfile
        import tempfile

        archive_path = download_file(url, self.bin_dir)
        install_dir = self.bin_dir / "aws-cli"
        install_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(archive_path, "r") as zf:
                zf.extractall(tmp)
            installer = next(
                (p for p in __import__("pathlib").Path(tmp).rglob("install")),
                None,
            )
            if installer is None:
                raise RuntimeError("AWS CLI installer script not found in archive.")
            os.chmod(installer, 0o755)
            subprocess.run(
                [str(installer), "-i", str(install_dir), "-b", str(self.bin_dir)],
                check=True,
            )

        archive_path.unlink()
        aws_bin = shutil.which("aws") or str(self.bin_dir / "aws")
        add_to_path(str(__import__("pathlib").Path(aws_bin).parent))
        print(f"{self.name} installed successfully.")
