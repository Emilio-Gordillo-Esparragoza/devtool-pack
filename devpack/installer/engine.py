"""Installer engine module."""

from devpack.installer.downloader import download_file
from devpack.installer.extractor import extract_archive
from devpack.env.path_manager import add_to_path
from devpack.utils.logger import get_logger

logger = get_logger(__name__)


def install_from_url(url: str, binary_name: str, install_dir: str) -> str:
    """Install a tool from a URL."""
    # Download the file
    archive_path = download_file(url, install_dir)

    # Extract the file
    extracted_path = extract_archive(archive_path, install_dir)

    # Clean up the archive
    archive_path.unlink()

    # Add to PATH
    add_to_path(install_dir)

    logger.info(f"Installed {binary_name} from {url}")
    return str(extracted_path)
