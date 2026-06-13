from pathlib import Path
from unittest.mock import patch, MagicMock

from devpack.tools.docker import DockerTool


def test_docker_tool_initialization():
    tool = DockerTool()
    assert tool.name == "docker"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_docker_tool_download_url():
    tool = DockerTool()
    assert "Docker%20Desktop" in tool.download_url


@patch("devpack.tools.docker.shutil.which")
def test_docker_tool_is_installed_false(mock_which):
    mock_which.return_value = None
    tool = DockerTool()
    assert not tool.is_installed()


@patch("devpack.tools.docker.shutil.which")
def test_docker_tool_is_installed_true(mock_which):
    mock_which.return_value = "/usr/bin/docker"
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
    with patch.object(tool, "is_installed", return_value=False):
        tool.install()

    mock_download_file.assert_called_once()
    mock_subprocess.run.assert_called_once()
    mock_add_to_path.assert_called_once()
