from pathlib import Path
from unittest.mock import patch, MagicMock

from devpack.tools.golang import GolangTool


def test_golang_tool_initialization():
    tool = GolangTool()
    assert tool.name == "go"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_golang_tool_download_url():
    tool = GolangTool()
    assert "go.dev" in tool.download_url
    assert "go1.21.5" in tool.download_url


@patch("devpack.tools.golang.download_file")
@patch("devpack.tools.golang.extract_archive")
@patch("devpack.tools.golang.add_to_path")
@patch("devpack.tools.golang.os")
def test_golang_tool_install(
    mock_os, mock_add_to_path, mock_extract_archive, mock_download_file
):
    mock_os.name = "nt"
    mock_archive = MagicMock()
    mock_download_file.return_value = mock_archive

    tool = GolangTool()
    with patch.object(tool, "is_installed", return_value=False):
        tool.install()

    mock_download_file.assert_called_once()
    mock_extract_archive.assert_called_once()
    mock_add_to_path.assert_called_once()
    mock_archive.unlink.assert_called_once()
