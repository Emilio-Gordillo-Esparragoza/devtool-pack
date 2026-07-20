from pathlib import Path
from unittest.mock import patch, MagicMock

from devpack.tools.golang import GolangTool


def test_golang_tool_initialization():
    tool = GolangTool()
    assert tool.name == "go"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_golang_download_url_windows():
    with patch("devpack.tools.base_tool._current_os", return_value="windows"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = GolangTool()
        assert "windows-amd64" in tool.download_url
        assert "go.dev" in tool.download_url


def test_golang_download_url_linux():
    with patch("devpack.tools.base_tool._current_os", return_value="linux"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = GolangTool()
        assert "linux-amd64" in tool.download_url
        assert "go.dev" in tool.download_url


def test_golang_download_url_darwin_arm64():
    with patch("devpack.tools.base_tool._current_os", return_value="darwin"), \
         patch("devpack.tools.base_tool._current_arch", return_value="arm64"):
        tool = GolangTool()
        assert "darwin-arm64" in tool.download_url


@patch("devpack.tools.golang.download_file")
@patch("devpack.tools.golang.extract_archive")
@patch("devpack.tools.golang.add_to_path")
def test_golang_tool_install(
    mock_add_to_path, mock_extract_archive, mock_download_file
):
    mock_archive = MagicMock()
    mock_download_file.return_value = mock_archive

    tool = GolangTool()
    fake_url = "https://go.dev/dl/go1.21.5.windows-amd64.zip"
    with patch.object(tool, "is_installed", return_value=False), \
         patch.object(tool, "_install_via_package_manager", return_value=False), \
         patch.object(type(tool), "download_url", new_callable=lambda: property(lambda self: fake_url)):
        tool.install()

    mock_download_file.assert_called_once()
    mock_extract_archive.assert_called_once()
    mock_add_to_path.assert_called_once()
    mock_archive.unlink.assert_called_once()
