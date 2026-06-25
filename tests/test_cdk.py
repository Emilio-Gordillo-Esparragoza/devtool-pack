from pathlib import Path
from unittest.mock import patch

from devpack.tools.cdk import CDKTool


def test_cdk_tool_initialization():
    tool = CDKTool()
    assert tool.name == "cdk"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_cdk_tool_download_url():
    tool = CDKTool()
    assert tool.download_url == ""


@patch("devpack.tools.cdk.shutil.which")
def test_cdk_tool_is_installed_false(mock_which):
    mock_which.return_value = None
    tool = CDKTool()
    assert not tool.is_installed()


@patch("devpack.tools.cdk.shutil.which")
def test_cdk_tool_is_installed_true(mock_which):
    mock_which.return_value = "/usr/local/bin/cdk"
    tool = CDKTool()
    assert tool.is_installed()


@patch("devpack.tools.cdk.subprocess.run")
@patch("devpack.tools.cdk.shutil.which")
@patch("devpack.tools.cdk.add_to_path")
def test_cdk_tool_install(mock_add_to_path, mock_which, mock_subprocess):
    mock_which.side_effect = ["/usr/bin/npm", "/usr/bin/npm", "/usr/local/bin/cdk"]
    tool = CDKTool()
    with patch.object(tool, "is_installed", return_value=False):
        tool.install()

    mock_subprocess.assert_called_once_with(
        ["/usr/bin/npm", "install", "-g", "aws-cdk"], check=True
    )
    mock_add_to_path.assert_called_once()
