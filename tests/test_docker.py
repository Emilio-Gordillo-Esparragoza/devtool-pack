from pathlib import Path
from unittest.mock import patch, MagicMock

from devpack.tools.docker import DockerTool


def test_docker_tool_initialization():
    tool = DockerTool()
    assert tool.name == "docker"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_docker_download_url_windows():
    with patch("devpack.tools.base_tool._current_os", return_value="windows"):
        tool = DockerTool()
        assert "Docker" in tool.download_url
        assert "desktop.docker.com" in tool.download_url


def test_docker_download_url_linux_empty():
    """Linux has no static binary URL — convenience script is used instead."""
    with (
        patch("devpack.tools.base_tool._current_os", return_value="linux"),
        patch("devpack.tools.base_tool._current_arch", return_value="amd64"),
    ):
        tool = DockerTool()
        assert tool.download_url == ""


@patch("devpack.tools.docker.shutil.which")
@patch("devpack.env.package_manager.get_package_manager")
@patch("devpack.env.package_manager.PackageManager.detect", return_value="none")
def test_docker_tool_is_installed_false(mock_detect, mock_get_pm, mock_which):
    mock_which.return_value = None
    mock_pm = mock_get_pm.return_value
    mock_pm.is_installed.return_value = False
    tool = DockerTool()
    assert not tool.is_installed()


@patch("devpack.tools.docker.shutil.which")
@patch("devpack.env.package_manager.get_package_manager")
@patch("devpack.env.package_manager.PackageManager.detect", return_value="none")
def test_docker_tool_is_installed_true(mock_detect, mock_get_pm, mock_which):
    mock_which.return_value = "/usr/bin/docker"
    mock_pm = mock_get_pm.return_value
    mock_pm.is_installed.return_value = False
    tool = DockerTool()
    assert tool.is_installed()


@patch("devpack.tools.docker.download_file")
@patch("devpack.tools.docker.subprocess")
@patch("devpack.tools.docker.shutil.which")
@patch("devpack.tools.docker.add_to_path")
@patch("devpack.tools.docker.os")
def test_docker_tool_install_windows(
    mock_os, mock_add_to_path, mock_which, mock_subprocess, mock_download_file
):
    mock_os.name = "nt"
    mock_which.return_value = "C:\\Program Files\\Docker\\docker.exe"
    mock_installer = MagicMock()
    mock_download_file.return_value = mock_installer

    tool = DockerTool()
    fake_url = "https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe"
    with (
        patch.object(tool, "is_installed", return_value=False),
        patch.object(tool, "_install_via_package_manager", return_value=False),
        patch.object(
            type(tool),
            "download_url",
            new_callable=lambda: property(lambda self: fake_url),
        ),
    ):
        tool.install()

    mock_download_file.assert_called_once()
    mock_subprocess.run.assert_called_once()
    mock_add_to_path.assert_called_once()


@patch("devpack.tools.docker.subprocess")
@patch("devpack.tools.docker.shutil")
@patch("devpack.tools.docker.add_to_path")
def test_docker_install_unix_linux(mock_add_to_path, mock_shutil, mock_subprocess):
    mock_shutil.which.return_value = (
        None  # skip the add_to_path(Path(...).parent) branch
    )

    tool = DockerTool()
    with patch("platform.system", return_value="Linux"):
        tool._install_unix()

    mock_subprocess.run.assert_called_once()


@patch("devpack.tools.docker.subprocess")
@patch("devpack.tools.docker.shutil")
@patch("devpack.tools.docker.add_to_path")
def test_docker_install_unix_macos_raises(
    mock_add_to_path, mock_shutil, mock_subprocess
):
    tool = DockerTool()
    import pytest

    with patch("platform.system", return_value="Darwin"):
        with pytest.raises(RuntimeError, match="Docker Desktop for macOS"):
            tool._install_unix()
