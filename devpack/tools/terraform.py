import os
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.installer.extractor import extract_archive
from devpack.env.path_manager import add_to_path


class TerraformTool(BaseTool):
    """Terraform tool installer."""

    config_key = "terraform"

    def __init__(self):
        super().__init__("terraform")

    @property
    def download_url(self) -> str:
        return self._resolve_url()

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        url = self.download_url
        if not url:
            raise RuntimeError("No download URL found for Terraform on this platform.")

        print(f"Downloading {self.name}...")
        archive_path = download_file(url, self.bin_dir)

        print(f"Extracting {self.name}...")
        extracted_path = extract_archive(archive_path, self.bin_dir)

        binary_name = "terraform.exe" if os.name == "nt" else "terraform"
        binary_path = extracted_path / binary_name
        if not binary_path.exists():
            binary_path = self.bin_dir / binary_name

        if os.name != "nt":
            os.chmod(binary_path, 0o755)

        if binary_path.parent != self.bin_dir:
            binary_path.rename(self.bin_dir / binary_name)

        archive_path.unlink()
        add_to_path(str(self.bin_dir))
        print(f"{self.name} installed successfully.")
