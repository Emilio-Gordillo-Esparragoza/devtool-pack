"""Tests for installer.downloader, installer.extractor and installer.engine."""
import zipfile
import tarfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from devpack.installer.downloader import download_file
from devpack.installer.extractor import extract_archive
from devpack.installer.engine import install_from_url


# ---------------------------------------------------------------------------
# downloader
# ---------------------------------------------------------------------------

@patch("devpack.installer.downloader.requests.get")
def test_download_file_success(mock_get, tmp_path):
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"data"]
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = download_file("https://example.com/tool.zip", tmp_path)

    assert result == tmp_path / "tool.zip"
    mock_get.assert_called_once_with("https://example.com/tool.zip", stream=True, timeout=30)


@patch("devpack.installer.downloader.requests.get")
def test_download_file_no_extension_filename(mock_get, tmp_path):
    """URLs with no filename default to 'downloaded_file'."""
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"data"]
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = download_file("https://example.com/download", tmp_path)
    assert result.name == "downloaded_file"


@patch("devpack.installer.downloader.requests.get")
def test_download_file_raises_on_error(mock_get, tmp_path):
    mock_get.side_effect = Exception("connection error")
    with pytest.raises(Exception, match="connection error"):
        download_file("https://example.com/tool.zip", tmp_path)


# ---------------------------------------------------------------------------
# extractor
# ---------------------------------------------------------------------------

def test_extract_zip(tmp_path):
    # Create a real zip file
    archive = tmp_path / "test.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("hello.txt", "hello")

    out_dir = tmp_path / "out"
    result = extract_archive(archive, out_dir)

    assert result == out_dir
    assert (out_dir / "hello.txt").exists()


def test_extract_tar_gz(tmp_path):
    archive = tmp_path / "test.tar.gz"
    content = tmp_path / "hello.txt"
    content.write_text("hello")
    with tarfile.open(archive, "w:gz") as tf:
        tf.add(content, arcname="hello.txt")

    out_dir = tmp_path / "out"
    result = extract_archive(archive, out_dir)

    assert result == out_dir
    assert (out_dir / "hello.txt").exists()


def test_extract_unsupported_format(tmp_path):
    archive = tmp_path / "test.7z"
    archive.write_bytes(b"fake")
    with pytest.raises(ValueError, match="Unsupported archive format"):
        extract_archive(archive, tmp_path / "out")


# ---------------------------------------------------------------------------
# engine
# ---------------------------------------------------------------------------

@patch("devpack.installer.engine.download_file")
@patch("devpack.installer.engine.extract_archive")
@patch("devpack.installer.engine.add_to_path")
def test_install_from_url(mock_add_to_path, mock_extract, mock_download):
    mock_archive = MagicMock()
    mock_download.return_value = mock_archive
    mock_extract.return_value = Path("/fake/extracted")

    result = install_from_url("https://example.com/tool.zip", "tool", "/fake/bin")

    assert result == str(Path("/fake/extracted"))
    mock_download.assert_called_once()
    mock_extract.assert_called_once()
    mock_archive.unlink.assert_called_once()
    mock_add_to_path.assert_called_once_with("/fake/bin")
