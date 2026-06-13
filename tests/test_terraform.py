from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from devpack.tools.terraform import TerraformTool


def test_terraform_tool_initialization():
    tool = TerraformTool()
    assert tool.name == "terraform"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_terraform_tool_is_installed_false_by_default():
    tool = TerraformTool()
    with patch.object(tool, "get_binary_path") as mock_get_path:
        mock_binary_path = MagicMock()
        mock_binary_path.is_file.return_value = False
        with patch("os.access", return_value=False):
            mock_get_path.return_value = mock_binary_path
            assert not tool.is_installed()


def test_terraform_tool_is_installed_true_when_binary_exists():
    tool = TerraformTool()
    with patch.object(tool, "get_binary_path") as mock_get_path:
        mock_binary_path = MagicMock()
        mock_binary_path.is_file.return_value = True
        with patch("os.access", return_value=True):
            mock_get_path.return_value = mock_binary_path
            assert tool.is_installed()


def test_terraform_download_url_windows():
    with patch("devpack.tools.base_tool._current_os", return_value="windows"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = TerraformTool()
        assert "windows_amd64" in tool.download_url
        assert "terraform" in tool.download_url


def test_terraform_download_url_linux():
    with patch("devpack.tools.base_tool._current_os", return_value="linux"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = TerraformTool()
        assert "linux_amd64" in tool.download_url


def test_terraform_download_url_darwin():
    with patch("devpack.tools.base_tool._current_os", return_value="darwin"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = TerraformTool()
        assert "darwin_amd64" in tool.download_url


@patch("devpack.tools.terraform.download_file")
@patch("devpack.tools.terraform.extract_archive")
@patch("devpack.tools.terraform.add_to_path")
@patch("devpack.tools.terraform.os")
def test_terraform_tool_install(
    mock_os, mock_add_to_path, mock_extract_archive, mock_download_file
):
    mock_archive_path = MagicMock()
    mock_download_file.return_value = mock_archive_path
    mock_extract_archive.return_value = Path("/fake/path/extracted")
    mock_os.name = "nt"

    tool = TerraformTool()
    fake_url = "https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_windows_amd64.zip"
    with patch.object(tool, "is_installed", return_value=False), \
         patch.object(type(tool), "download_url", new_callable=lambda: property(lambda self: fake_url)):
        tool.install()

    mock_download_file.assert_called_once()
    mock_extract_archive.assert_called_once()
    mock_add_to_path.assert_called_once()
    mock_archive_path.unlink.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
