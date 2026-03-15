import zipfile
import tarfile
from pathlib import Path
from typing import Union
from devpack.utils.logger import get_logger

logger = get_logger(__name__)


def extract_archive(
    archive_path: Union[str, Path], extract_dir: Union[str, Path]
) -> Path:
    """Extract an archive (zip or tar) to the specified directory."""
    archive_path = Path(archive_path)
    extract_dir = Path(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Extracting {archive_path} to {extract_dir}")

    if archive_path.suffix == ".zip":
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
    elif archive_path.suffix in [".tar", ".gz", ".bz2", ".xz"]:
        # Note: tarfile can handle .tar.gz, .tar.bz2, .tar.xz
        with tarfile.open(archive_path, "r:*") as tar_ref:
            tar_ref.extractall(extract_dir)
    else:
        raise ValueError(f"Unsupported archive format: {archive_path.suffix}")

    logger.info(f"Extraction completed: {extract_dir}")
    return extract_dir
