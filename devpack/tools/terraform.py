import os
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.installer.extractor import extract_archive
from devpack.env.path_manager import add_to_path


class TerraformTool(BaseTool):
    """Terraform tool installer."""

    def __init__(self):
        super().__init__("terraform")

    @property
    def download_url(self) -> str:
        # For simplicity, we'll use a placeholder URL. In reality, this would be dynamic based on OS/arch.
        # We'll use a version that we know exists for demonstration.
        return "https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_windows_amd64.zip"

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        print(f"Downloading {self.name}...")
        archive_path = download_file(self.download_url, self.bin_dir)

        print(f"Extracting {self.name}...")
        extracted_path = extract_archive(archive_path, self.bin_dir)

        # The extracted file might be in a subdirectory, so we look for the binary
        binary_name = "terraform.exe" if os.name == "nt" else "terraform"
        binary_path = extracted_path / binary_name
        if not binary_path.exists():
            # If not found in the extracted directory, look in the bin_dir
            binary_path = self.bin_dir / binary_name

        # Ensure the binary is executable
        if os.name != "nt":
            os.chmod(binary_path, 0o755)

        # Move the binary to the bin_dir if it's not already there
        if binary_path.parent != self.bin_dir:
            binary_path.rename(self.bin_dir / binary_name)

        # Clean up the archive
        archive_path.unlink()

        # Add to PATH
        add_to_path(str(self.bin_dir))

        print(f"{self.name} installed successfully.")
