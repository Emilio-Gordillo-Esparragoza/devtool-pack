from pathlib import Path
from unittest.mock import patch, MagicMock

from devpack.tools.sam import SamTool


def test_sam_tool_initialization():
    tool = SamTool()
    assert tool.name == "sam"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_sam_download_url_windows():
    with patch("devpack.tools.base_tool._current_os", return_value="windows"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = SamTool()
        assert "aws-sam-cli" in tool.download_url
        assert "windows" in tool.download_url


def test_sam_download_url_linux():
    with patch("devpack.tools.base_tool._current_os", return_value="linux"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = SamTool()
        assert "aws-sam-cli" in tool.download_url
        assert "linux" in tool.download_url


def test_sam_download_url_darwin():
    with patch("devpack.tools.base_tool._current_os", return_value="darwin"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = SamTool()
        assert "aws-sam-cli" in tool.download_url
        assert "macos" in tool.download_url


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
    fake_url = "https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-windows-x86_64.zip"
    with patch.object(tool, "is_installed", return_value=False), \
         patch.object(tool, "_install_via_package_manager", return_value=False), \
         patch.object(type(tool), "download_url", new_callable=lambda: property(lambda self: fake_url)):
        tool.install()

    mock_download_file.assert_called_once()
    mock_extract_archive.assert_called_once()
    mock_add_to_path.assert_called_once()
    mock_archive.unlink.assert_called_once()
