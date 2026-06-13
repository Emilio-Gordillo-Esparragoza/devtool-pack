import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from devpack.tools.git import GitTool


def test_git_tool_initialization():
    tool = GitTool()
    assert tool.name == "git"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_git_download_url_windows():
    with patch("devpack.tools.base_tool._current_os", return_value="windows"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = GitTool()
        assert "PortableGit" in tool.download_url
        assert tool.download_url.endswith(".7z.exe")


def test_git_download_url_linux_empty():
    """Linux uses the system package manager — no static binary URL."""
    with patch("devpack.tools.base_tool._current_os", return_value="linux"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = GitTool()
        assert tool.download_url == ""


@patch("devpack.tools.git.shutil.which")
def test_git_tool_is_installed_via_system(mock_which):
    mock_which.return_value = "C:\\Program Files\\Git\\bin\\git.exe"
    tool = GitTool()
    with patch.object(tool, "is_installed", return_value=False):
        assert tool.download_url is not None


@patch("devpack.tools.git.download_file")
@patch("devpack.tools.git.add_to_path")
@patch("devpack.tools.git.os")
@patch("devpack.tools.git.subprocess")
def test_git_tool_install(
    mock_subprocess, mock_os, mock_add_to_path, mock_download_file
):
    mock_os.name = "nt"
    mock_installer = MagicMock()
    mock_download_file.return_value = mock_installer

    tool = GitTool()
    fake_url = "https://github.com/git-for-windows/git/releases/download/v2.41.0.windows.3/PortableGit-2.41.0.3-64-bit.7z.exe"
    with patch.object(tool, "is_installed", return_value=False), \
         patch("devpack.tools.git.shutil.which", return_value=None), \
         patch.object(type(tool), "download_url", new_callable=lambda: property(lambda self: fake_url)):
        tool.install()

    mock_download_file.assert_called_once()
    mock_subprocess.run.assert_called_once()
    mock_add_to_path.assert_called_once()


@patch("devpack.tools.git.subprocess")
@patch("devpack.tools.git.shutil")
@patch("devpack.tools.git.add_to_path")
def test_git_install_unix_apt(mock_add_to_path, mock_shutil, mock_subprocess):
    mock_shutil.which.side_effect = lambda cmd: "/usr/bin/apt-get" if cmd == "apt-get" else None
    tool = GitTool()
    with patch("platform.system", return_value="Linux"):
        tool._install_unix()
    mock_subprocess.run.assert_called_once()
    assert "apt-get" in mock_subprocess.run.call_args[0][0]


@patch("devpack.tools.git.subprocess")
@patch("devpack.tools.git.shutil")
@patch("devpack.tools.git.add_to_path")
def test_git_install_unix_pacman(mock_add_to_path, mock_shutil, mock_subprocess):
    """Arch-based distros (Arch, CachyOS, Manjaro) use pacman."""
    mock_shutil.which.side_effect = lambda cmd: "/usr/bin/pacman" if cmd == "pacman" else None
    tool = GitTool()
    with patch("platform.system", return_value="Linux"):
        tool._install_unix()
    mock_subprocess.run.assert_called_once()
    assert "pacman" in mock_subprocess.run.call_args[0][0]


@patch("devpack.tools.git.subprocess")
@patch("devpack.tools.git.shutil")
@patch("devpack.tools.git.add_to_path")
def test_git_install_unix_dnf(mock_add_to_path, mock_shutil, mock_subprocess):
    """Fedora/RHEL use dnf."""
    mock_shutil.which.side_effect = lambda cmd: "/usr/bin/dnf" if cmd == "dnf" else None
    tool = GitTool()
    with patch("platform.system", return_value="Linux"):
        tool._install_unix()
    mock_subprocess.run.assert_called_once()
    assert "dnf" in mock_subprocess.run.call_args[0][0]


@patch("devpack.tools.git.subprocess")
@patch("devpack.tools.git.shutil")
@patch("devpack.tools.git.add_to_path")
def test_git_install_unix_brew(mock_add_to_path, mock_shutil, mock_subprocess):
    tool = GitTool()
    with patch("platform.system", return_value="Darwin"):
        tool._install_unix()
    mock_subprocess.run.assert_called_once()
    assert "brew" in mock_subprocess.run.call_args[0][0]


@patch("devpack.tools.git.subprocess")
@patch("devpack.tools.git.shutil")
@patch("devpack.tools.git.add_to_path")
def test_git_install_unix_no_package_manager(mock_add_to_path, mock_shutil, mock_subprocess):
    mock_shutil.which.return_value = None
    tool = GitTool()
    with patch("platform.system", return_value="Linux"):
        with pytest.raises(RuntimeError, match="Unsupported Linux package manager"):
            tool._install_unix()
