from pathlib import Path
from unittest.mock import patch, MagicMock

from devpack.tools.sam import SamTool


def test_sam_tool_initialization():
    tool = SamTool()
    assert tool.name == "sam"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_sam_tool_download_url():
    tool = SamTool()
    assert "aws-sam-cli" in tool.download_url


@patch("devpack.tools.sam.download_file")
@patch("devpack.tools.sam.extract_archive")
@patch("devpack.tools.sam.add_to_path")
@patch("devpack.tools.sam.os")
def test_sam_tool_install(
    mock_os, mock_add_to_path, mock_extract_archive, mock_download_file
):
    mock_os.name = "nt"
    mock_archive = MagicMock()
    mock_download_file.return_value = mock_archive
    mock_extract_archive.return_value = Path("/fake/extracted")

    tool = SamTool()
    with patch.object(tool, "is_installed", return_value=False):
        tool.install()

    mock_download_file.assert_called_once()
    mock_extract_archive.assert_called_once()
    mock_add_to_path.assert_called_once()
    mock_archive.unlink.assert_called_once()
