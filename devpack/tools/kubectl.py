import os
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.env.path_manager import add_to_path


class KubectlTool(BaseTool):
    """Kubectl tool installer."""

    config_key = "kubectl"

    def __init__(self):
        super().__init__("kubectl")

    @property
    def download_url(self) -> str:
        return self._resolve_url()

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        url = self.download_url
        if not url:
            raise RuntimeError("No download URL found for kubectl on this platform.")

        print(f"Downloading {self.name}...")
        binary_path = download_file(url, self.bin_dir)

        if os.name != "nt":
            os.chmod(binary_path, 0o755)

        add_to_path(str(self.bin_dir))
        print(f"{self.name} installed successfully.")
