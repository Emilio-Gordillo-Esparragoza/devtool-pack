from pathlib import Path
from unittest.mock import patch

from devpack.tools.localstack import LocalStackTool


def test_localstack_tool_initialization():
    tool = LocalStackTool()
    assert tool.name == "localstack"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_localstack_tool_download_url():
    tool = LocalStackTool()
    assert tool.download_url == ""


@patch("devpack.tools.localstack.shutil.which")
def test_localstack_tool_is_installed_false(mock_which):
    mock_which.return_value = None
    tool = LocalStackTool()
    assert not tool.is_installed()


@patch("devpack.tools.localstack.shutil.which")
def test_localstack_tool_is_installed_true(mock_which):
    mock_which.return_value = "/usr/local/bin/localstack"
    tool = LocalStackTool()
    assert tool.is_installed()


@patch("devpack.tools.localstack.subprocess.run")
@patch("devpack.tools.localstack.shutil.which")
@patch("devpack.tools.localstack.add_to_path")
def test_localstack_tool_install(mock_add_to_path, mock_which, mock_subprocess):
    mock_which.return_value = "/usr/local/bin/localstack"
    tool = LocalStackTool()
    with patch.object(tool, "is_installed", return_value=False):
        tool.install()

    mock_subprocess.assert_called_once()
    mock_add_to_path.assert_called_once()
