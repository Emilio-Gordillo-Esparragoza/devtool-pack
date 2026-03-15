import requests
from pathlib import Path
from devpack.utils.logger import get_logger

logger = get_logger(__name__)


def download_file(url: str, destination_dir: Path) -> Path:
    """Download a file from URL to destination directory."""
    destination_dir.mkdir(parents=True, exist_ok=True)

    # Extract filename from URL
    filename = url.split("/")[-1]
    if not filename or "." not in filename:
        # Generate a filename if URL doesn't have one
        filename = "downloaded_file"

    file_path = destination_dir / filename

    logger.info(f"Downloading {url} to {file_path}")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Download completed: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        raise
