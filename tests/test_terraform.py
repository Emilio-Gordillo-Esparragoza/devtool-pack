from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from devpack.tools.terraform import TerraformTool


def test_terraform_tool_initialization():
    """Test that TerraformTool initializes correctly."""
    tool = TerraformTool()
    assert tool.name == "terraform"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_terraform_tool_is_installed_false_by_default():
    """Test that is_installed returns False by default."""
    tool = TerraformTool()
    # Mock the binary path to not exist and not be executable
    with patch.object(tool, "get_binary_path") as mock_get_path:
        mock_binary_path = MagicMock()
        mock_binary_path.is_file.return_value = False
        # Mock os.access to return False for both F_OK and X_OK
        with patch("os.access", return_value=False):
            mock_get_path.return_value = mock_binary_path
            assert not tool.is_installed()


def test_terraform_tool_is_installed_true_when_binary_exists():
    """Test that is_installed returns True when binary exists and is executable."""
    tool = TerraformTool()
    # Mock the binary path to exist and be executable
    with patch.object(tool, "get_binary_path") as mock_get_path:
        mock_binary_path = MagicMock()
        mock_binary_path.is_file.return_value = True
        # Mock os.access to return True for both F_OK and X_OK
        with patch("os.access", return_value=True):
            mock_get_path.return_value = mock_binary_path
            assert tool.is_installed()


def test_terraform_tool_download_url():
    """Test that download_url returns expected URL."""
    tool = TerraformTool()
    expected_url = "https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_windows_amd64.zip"
    assert tool.download_url == expected_url


@patch("devpack.tools.terraform.download_file")
@patch("devpack.tools.terraform.extract_archive")
@patch("devpack.tools.terraform.add_to_path")
@patch("devpack.tools.terraform.os")
def test_terraform_tool_install(
    mock_os, mock_add_to_path, mock_extract_archive, mock_download_file
):
    """Test the install method of TerraformTool."""
    # Setup mocks
    mock_archive_path = MagicMock()
    mock_download_file.return_value = mock_archive_path
    mock_extract_archive.return_value = Path("/fake/path/extracted")
    mock_os.name = "nt"

    tool = TerraformTool()

    # Mock is_installed to return False so installation proceeds
    with patch.object(tool, "is_installed", return_value=False):
        tool.install()

    # Verify the methods were called
    mock_download_file.assert_called_once()
    mock_extract_archive.assert_called_once()
    mock_add_to_path.assert_called_once()
    mock_archive_path.unlink.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
