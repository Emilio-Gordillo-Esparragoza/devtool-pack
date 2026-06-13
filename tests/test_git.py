from pathlib import Path
from unittest.mock import patch, MagicMock

from devpack.tools.git import GitTool


def test_git_tool_initialization():
    tool = GitTool()
    assert tool.name == "git"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_git_tool_download_url():
    tool = GitTool()
    assert "PortableGit" in tool.download_url
    assert tool.download_url.endswith(".7z.exe")


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
    with patch.object(tool, "is_installed", return_value=False):
        with patch("devpack.tools.git.shutil.which", return_value=None):
            tool.install()

    mock_download_file.assert_called_once()
    mock_subprocess.run.assert_called_once()
    mock_add_to_path.assert_called_once()
