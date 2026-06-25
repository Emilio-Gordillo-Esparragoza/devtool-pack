from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.installer.extractor import extract_archive
from devpack.env.path_manager import add_to_path


class GolangTool(BaseTool):
    """Go (Golang) tool installer."""

    config_key = "golang"

    package_names = {
        "apt": "golang-go",
        "pacman": "go",
        "dnf": "golang",
        "yum": "golang",
        "brew": "go",
        "choco": "golang",
        "winget": "GoLang.Go",
    }

    def __init__(self):
        super().__init__("go")

    @property
    def download_url(self) -> str:
        return self._resolve_url()

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        if self._install_via_package_manager():
            go_binary = self.bin_dir / "go" / "bin" / self.binary_name
            if go_binary.exists():
                add_to_path(str(go_binary.parent))
            else:
                add_to_path(str(self.bin_dir))
            print(f"{self.name} installed successfully.")
            return

        url = self.download_url
        if not url:
            raise RuntimeError("No download URL found for Go on this platform.")

        print(f"Downloading {self.name}...")
        archive_path = download_file(url, self.bin_dir)

        print(f"Extracting {self.name}...")
        extract_archive(archive_path, self.bin_dir)

        go_binary = self.bin_dir / "go" / "bin" / self.binary_name
        if go_binary.exists():
            add_to_path(str(go_binary.parent))
        else:
            add_to_path(str(self.bin_dir))

        archive_path.unlink()
        print(f"{self.name} installed successfully.")
