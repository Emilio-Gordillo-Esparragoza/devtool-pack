import os
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.env.path_manager import add_to_path


class KubectlTool(BaseTool):
    """Kubectl tool installer."""

    def __init__(self):
        super().__init__("kubectl")

    @property
    def download_url(self) -> str:
        # Kubectl for Windows
        return "https://dl.k8s.io/release/v1.27.0/bin/windows/amd64/kubectl.exe"

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        print(f"Downloading {self.name}...")
        binary_path = download_file(self.download_url, self.bin_dir)

        # Ensure the binary is executable
        if os.name != "nt":
            os.chmod(binary_path, 0o755)

        # Add to PATH
        add_to_path(str(self.bin_dir))

        print(f"{self.name} installed successfully.")
