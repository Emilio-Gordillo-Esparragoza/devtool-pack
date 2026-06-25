"""Node.js tool installer."""

import os
import shutil
from pathlib import Path
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.installer.extractor import extract_archive
from devpack.env.path_manager import add_to_path


class NodeTool(BaseTool):
    """Node.js tool installer."""

    config_key = "node"

    package_names = {
        "apt": "nodejs",
        "pacman": "nodejs",
        "dnf": "nodejs",
        "yum": "nodejs",
        "brew": "node",
        "choco": "nodejs",
        "winget": "OpenJS.NodeJS",
    }

    def __init__(self):
        super().__init__("node")

    @property
    def download_url(self) -> str:
        return self._resolve_url()

    def is_installed(self) -> bool:
        return (
            shutil.which("node") is not None or self._is_installed_via_package_manager()
        )

    def get_binary_path(self) -> Path:
        path = shutil.which("node")
        return Path(path) if path else self.bin_dir / self.binary_name

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        if self._install_via_package_manager():
            print(f"{self.name} installed successfully.")
            return

        url = self.download_url
        if not url:
            raise RuntimeError("No download URL found for Node.js on this platform.")

        print(f"Downloading {self.name}...")
        archive_path = download_file(url, self.bin_dir)

        print(f"Extracting {self.name}...")
        extracted_path = extract_archive(archive_path, self.bin_dir)

        # Node.js binary is typically in the extracted folder's bin directory
        node_binary = extracted_path / "bin" / self.binary_name
        if os.name == "nt":
            node_binary = extracted_path / f"{self.binary_name}.exe"

        if not node_binary.exists():
            # Try alternative locations
            for p in extracted_path.rglob(self.binary_name):
                if p.is_file() and os.access(p, os.X_OK):
                    node_binary = p
                    break

        if node_binary.exists():
            if os.name != "nt":
                os.chmod(node_binary, 0o755)
            if node_binary.parent != self.bin_dir:
                node_binary.rename(self.bin_dir / self.binary_name)

        archive_path.unlink()
        add_to_path(str(self.bin_dir))
        print(f"{self.name} installed successfully.")
