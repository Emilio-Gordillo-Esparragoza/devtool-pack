"""Tests for doctor.validator."""
from unittest.mock import patch, MagicMock

from devpack.doctor.validator import validate_tool, validate_all


def _make_tool(installed: bool, binary_path="/usr/local/bin/terraform"):
    tool = MagicMock()
    tool.is_installed.return_value = installed
    tool.get_binary_path.return_value = binary_path
    return tool


def test_validate_tool_installed_and_in_path():
    tool = _make_tool(True)
    with patch("devpack.doctor.validator.shutil.which", return_value="/usr/local/bin/terraform"):
        result = validate_tool("terraform", tool)
    assert result is True


def test_validate_tool_installed_not_in_path():
    tool = _make_tool(True)
    with patch("devpack.doctor.validator.shutil.which", return_value=None):
        result = validate_tool("terraform", tool)
    assert result is False


def test_validate_tool_not_installed():
    tool = _make_tool(False)
    with patch("devpack.doctor.validator.shutil.which", return_value=None):
        result = validate_tool("terraform", tool)
    assert result is False


@patch("devpack.doctor.validator.TerraformTool")
@patch("devpack.doctor.validator.AWSCLITool")
@patch("devpack.doctor.validator.KubectlTool")
@patch("devpack.doctor.validator.GitTool")
@patch("devpack.doctor.validator.SamTool")
@patch("devpack.doctor.validator.LocalStackTool")
@patch("devpack.doctor.validator.CDKTool")
@patch("devpack.doctor.validator.DockerTool")
@patch("devpack.doctor.validator.RustTool")
@patch("devpack.doctor.validator.GolangTool")
def test_validate_all_all_valid(
    MockGo, MockRust, MockDocker, MockCDK, MockLS,
    MockSam, MockGit, MockKubectl, MockAws, MockTf,
):
    for Mock in (MockGo, MockRust, MockDocker, MockCDK, MockLS,
                 MockSam, MockGit, MockKubectl, MockAws, MockTf):
        instance = MagicMock()
        instance.is_installed.return_value = True
        instance.get_binary_path.return_value = "/usr/local/bin/tool"
        Mock.return_value = instance

    with patch("devpack.doctor.validator.shutil.which", return_value="/usr/local/bin/tool"):
        validate_all()  # should not raise


@patch("devpack.doctor.validator.TerraformTool")
@patch("devpack.doctor.validator.AWSCLITool")
@patch("devpack.doctor.validator.KubectlTool")
@patch("devpack.doctor.validator.GitTool")
@patch("devpack.doctor.validator.SamTool")
@patch("devpack.doctor.validator.LocalStackTool")
@patch("devpack.doctor.validator.CDKTool")
@patch("devpack.doctor.validator.DockerTool")
@patch("devpack.doctor.validator.RustTool")
@patch("devpack.doctor.validator.GolangTool")
def test_validate_all_some_missing(
    MockGo, MockRust, MockDocker, MockCDK, MockLS,
    MockSam, MockGit, MockKubectl, MockAws, MockTf,
):
    for Mock in (MockGo, MockRust, MockDocker, MockCDK, MockLS,
                 MockSam, MockGit, MockKubectl, MockAws, MockTf):
        instance = MagicMock()
        instance.is_installed.return_value = False
        instance.get_binary_path.return_value = "/usr/local/bin/tool"
        Mock.return_value = instance

    with patch("devpack.doctor.validator.shutil.which", return_value=None):
        validate_all()  # should not raise
