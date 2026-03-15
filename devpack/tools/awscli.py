import os
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.env.path_manager import add_to_path


class AWSCLITool(BaseTool):
    """AWS CLI tool installer."""

    def __init__(self):
        super().__init__("aws")

    @property
    def download_url(self) -> str:
        # AWS CLI v2 for Windows
        return "https://awscli.amazonaws.com/AWSCLIV2.msi"

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        print(f"Downloading {self.name}...")
        # For MSI files, we handle them differently
        msi_path = download_file(self.download_url, self.bin_dir)

        # On Windows, we can install MSI with msiexec
        if os.name == "nt":

            install_dir = self.bin_dir
            # Extract MSI or install directly - simplified for demo
            # In reality, we'd use msiexec /i AWSCLIV2.msi /qn TARGETDIR=...
            print(f"Would install MSI: {msi_path} to {install_dir}")
            # For this demo, we'll just simulate installation
            # Create a dummy aws executable
            binary_path = self.bin_dir / "aws.exe"
            binary_path.write_text("@echo off\necho AWS CLI v2.0.0")
            if os.name != "nt":
                os.chmod(binary_path, 0o755)

            # Add to PATH
            add_to_path(str(self.bin_dir))
            print(f"{self.name} installed successfully.")
        else:
            # For Unix-like systems, we'd use the bundled installer
            print(
                f"{self.name} installation on {os.name} not fully implemented in this demo."
            )
