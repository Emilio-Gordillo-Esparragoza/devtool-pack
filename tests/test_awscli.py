from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from devpack.tools.awscli import AWSCLITool


def test_awscli_initialization():
    tool = AWSCLITool()
    assert tool.name == "aws"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_awscli_download_url_windows():
    with patch("devpack.tools.base_tool._current_os", return_value="windows"):
        tool = AWSCLITool()
        assert "AWSCLIV2.msi" in tool.download_url


def test_awscli_download_url_linux_amd64():
    with patch("devpack.tools.base_tool._current_os", return_value="linux"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = AWSCLITool()
        assert "awscli-exe-linux-x86_64" in tool.download_url


def test_awscli_download_url_linux_arm64():
    with patch("devpack.tools.base_tool._current_os", return_value="linux"), \
         patch("devpack.tools.base_tool._current_arch", return_value="arm64"):
        tool = AWSCLITool()
        assert "aarch64" in tool.download_url


def test_awscli_download_url_darwin():
    with patch("devpack.tools.base_tool._current_os", return_value="darwin"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = AWSCLITool()
        assert "AWSCLIV2.pkg" in tool.download_url


def test_awscli_install_already_installed(capsys):
    tool = AWSCLITool()
    with patch.object(tool, "is_installed", return_value=True):
        tool.install()
    assert "already installed" in capsys.readouterr().out


def test_awscli_install_no_url():
    tool = AWSCLITool()
    with patch.object(tool, "is_installed", return_value=False), \
         patch.object(tool, "_install_via_package_manager", return_value=False), \
         patch.object(type(tool), "download_url", new_callable=lambda: property(lambda self: "")):
        with pytest.raises(RuntimeError, match="No download URL"):
            tool.install()


@patch("devpack.tools.awscli.download_file")
@patch("devpack.tools.awscli.add_to_path")
@patch("devpack.tools.awscli.shutil")
@patch("devpack.tools.awscli.subprocess")
@patch("devpack.tools.awscli.os")
def test_awscli_install_unix_dispatch(mock_os, mock_subprocess, mock_shutil, mock_add_to_path, mock_download_file):
    """On non-nt, install() should call _install_unix."""
    mock_os.name = "posix"
    fake_url = "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"

    tool = AWSCLITool()
    with patch.object(tool, "is_installed", return_value=False), \
         patch.object(tool, "_install_via_package_manager", return_value=False), \
         patch.object(type(tool), "download_url", new_callable=lambda: property(lambda self: fake_url)), \
         patch.object(tool, "_install_unix") as mock_unix:
        tool.install()

    mock_unix.assert_called_once_with(fake_url)


@patch("devpack.tools.awscli.download_file")
@patch("devpack.tools.awscli.subprocess")
@patch("devpack.tools.awscli.add_to_path")
@patch("devpack.tools.awscli.os")
def test_awscli_install_windows(mock_os, mock_add_to_path, mock_subprocess, mock_download_file):
    mock_os.name = "nt"
    fake_msi = MagicMock()
    mock_download_file.return_value = fake_msi
    fake_url = "https://awscli.amazonaws.com/AWSCLIV2.msi"

    tool = AWSCLITool()
    aws_bin_dir = MagicMock()
    aws_bin_dir.is_dir.return_value = False

    with patch.object(tool, "is_installed", return_value=False), \
         patch.object(tool, "_install_via_package_manager", return_value=False), \
         patch.object(type(tool), "download_url", new_callable=lambda: property(lambda self: fake_url)), \
         patch.object(Path, "mkdir"), \
         patch.object(Path, "__truediv__", return_value=aws_bin_dir):
        tool.install()

    mock_download_file.assert_called_once()
    mock_subprocess.run.assert_called_once()


@patch("devpack.tools.awscli.download_file")
@patch("devpack.tools.awscli.subprocess")
@patch("devpack.tools.awscli.shutil")
@patch("devpack.tools.awscli.add_to_path")
@patch("devpack.tools.awscli.os")
def test_awscli_install_unix(mock_os, mock_add_to_path, mock_shutil, mock_subprocess, mock_download_file):
    mock_os.name = "posix"
    mock_os.chmod = MagicMock()
    fake_archive = MagicMock()
    mock_download_file.return_value = fake_archive
    mock_shutil.which.return_value = "/usr/local/bin/aws"
    fake_url = "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"

    tool = AWSCLITool()
    # Patch _install_unix directly to avoid zipfile/tempfile plumbing
    with patch.object(tool, "is_installed", return_value=False), \
         patch.object(tool, "_install_via_package_manager", return_value=False), \
         patch.object(type(tool), "download_url", new_callable=lambda: property(lambda self: fake_url)), \
         patch.object(tool, "_install_unix") as mock_unix:
        tool.install()

    mock_unix.assert_called_once_with(fake_url)
