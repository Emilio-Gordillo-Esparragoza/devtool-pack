import os
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.installer.extractor import extract_archive
from devpack.env.path_manager import add_to_path


class GolangTool(BaseTool):
    """Go (Golang) tool installer."""

    def __init__(self):
        super().__init__("go")

    @property
    def download_url(self) -> str:
        if os.name == "nt":
            return "https://go.dev/dl/go1.21.5.windows-amd64.zip"
        return "https://go.dev/dl/go1.21.5.linux-amd64.tar.gz"

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        print(f"Downloading {self.name}...")
        archive_path = download_file(self.download_url, self.bin_dir)

        print(f"Extracting {self.name}...")
        extract_archive(archive_path, self.bin_dir)

        go_binary = self.bin_dir / "go" / "bin" / self.binary_name
        if go_binary.exists():
            add_to_path(str(go_binary.parent))
        else:
            add_to_path(str(self.bin_dir))

        archive_path.unlink()
        print(f"{self.name} installed successfully.")
