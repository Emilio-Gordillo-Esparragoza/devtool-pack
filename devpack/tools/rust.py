import os
import subprocess
import shutil
from pathlib import Path
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.env.path_manager import add_to_path


class RustTool(BaseTool):
    """Rust tool installer (rustup)."""

    config_key = "rust"

    def __init__(self):
        super().__init__("rustc")

    @property
    def download_url(self) -> str:
        return self._resolve_url()

    def is_installed(self) -> bool:
        return shutil.which("rustc") is not None

    def get_binary_path(self) -> Path:
        path = shutil.which("rustc")
        return Path(path) if path else self.bin_dir / self.binary_name

    def install(self) -> None:
        if self.is_installed():
            print("Rust is already installed.")
            return

        url = self.download_url
        if not url:
            raise RuntimeError("No download URL found for Rust on this platform.")

        print("Downloading rustup-init...")
        rustup_init = download_file(url, self.bin_dir)

        if os.name != "nt":
            os.chmod(rustup_init, 0o755)

        print("Running rustup-init...")
        subprocess.run([str(rustup_init), "-y"], check=True)

        cargo_bin = Path.home() / ".cargo" / "bin"
        if cargo_bin.exists():
            add_to_path(str(cargo_bin))

        print("Rust installed successfully.")
