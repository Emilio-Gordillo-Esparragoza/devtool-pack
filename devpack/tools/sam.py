import os
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.installer.extractor import extract_archive
from devpack.env.path_manager import add_to_path


class SamTool(BaseTool):
    """AWS SAM CLI tool installer."""

    def __init__(self):
        super().__init__("sam")

    @property
    def download_url(self) -> str:
        return (
            "https://github.com/aws/aws-sam-cli/releases/latest/download/"
            "aws-sam-cli-windows-x86_64.zip"
        )

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        print(f"Downloading {self.name}...")
        archive_path = download_file(self.download_url, self.bin_dir)

        print(f"Extracting {self.name}...")
        extracted_path = extract_archive(archive_path, self.bin_dir)

        binary_name = "sam.exe" if os.name == "nt" else "sam"
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
