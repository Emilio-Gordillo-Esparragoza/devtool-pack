"""Tests for CLI commands: install, list_, doctor."""
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from devpack.cli import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# install command
# ---------------------------------------------------------------------------

def test_install_known_tool():
    with patch("devpack.commands.install.TerraformTool") as MockTool:
        instance = MagicMock()
        MockTool.return_value = instance
        result = runner.invoke(app, ["install", "terraform"])
    assert result.exit_code == 0
    instance.install.assert_called_once()


def test_install_unknown_tool():
    result = runner.invoke(app, ["install", "notarealthing"])
    assert result.exit_code != 0
    assert "Unknown tool" in result.output


def test_install_all_known_tools():
    tools = [
        "terraform", "awscli", "kubectl", "git", "sam",
        "localstack", "cdk", "docker", "rust", "golang", "node",
    ]
    for tool_name in tools:
        with patch(f"devpack.commands.install.{_tool_class(tool_name)}") as MockTool:
            instance = MagicMock()
            MockTool.return_value = instance
            result = runner.invoke(app, ["install", tool_name])
        assert result.exit_code == 0, f"Failed for {tool_name}: {result.output}"
        instance.install.assert_called_once()


def _tool_class(name: str) -> str:
    mapping = {
        "terraform": "TerraformTool",
        "awscli": "AWSCLITool",
        "kubectl": "KubectlTool",
        "git": "GitTool",
        "sam": "SamTool",
        "localstack": "LocalStackTool",
        "cdk": "CDKTool",
        "docker": "DockerTool",
        "rust": "RustTool",
        "golang": "GolangTool",
        "node": "NodeTool",
    }
    return mapping[name]


# ---------------------------------------------------------------------------
# list command
# ---------------------------------------------------------------------------

def test_list_tools_output():
    result = runner.invoke(app, ["list-tools"])
    assert result.exit_code == 0
    for tool in ("terraform", "awscli", "kubectl", "git", "sam",
                 "localstack", "cdk", "docker", "rust", "golang", "node"):
        assert tool in result.output


# ---------------------------------------------------------------------------
# doctor command
# ---------------------------------------------------------------------------

def test_doctor_command():
    with patch("devpack.commands.doctor.validate_all") as mock_validate:
        result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    mock_validate.assert_called_once()
