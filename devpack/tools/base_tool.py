from abc import ABC, abstractmethod
import os
from pathlib import Path


class BaseTool(ABC):
    """Abstract base class for all tools."""

    def __init__(self, name: str):
        self.name = name
        self.bin_dir = Path.home() / ".devpack" / "bin"
        self.bin_dir.mkdir(parents=True, exist_ok=True)

    @property
    def binary_name(self) -> str:
        """The name of the binary file, including extension if on Windows."""
        if os.name == "nt":
            return f"{self.name}.exe"
        return self.name

    @property
    @abstractmethod
    def download_url(self) -> str:
        """URL to download the tool binary."""
        pass

    @abstractmethod
    def install(self) -> None:
        """Download and install the tool."""
        pass

    def is_installed(self) -> bool:
        """Check if the tool is installed in the bin directory."""
        binary_path = self.get_binary_path()
        return binary_path.is_file() and os.access(binary_path, os.X_OK)

    def get_binary_path(self) -> Path:
        """Get the full path to the installed binary."""
        return self.bin_dir / self.binary_name
