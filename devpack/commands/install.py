import typer
from devpack.tools.terraform import TerraformTool
from devpack.tools.awscli import AWSCLITool
from devpack.tools.kubectl import KubectlTool


def install(
    tool: str = typer.Argument(
        ..., help="Tool to install (terraform, awscli, kubectl)"
    ),
):
    """Install a DevOps tool."""
    tool_map = {
        "terraform": TerraformTool(),
        "awscli": AWSCLITool(),
        "kubectl": KubectlTool(),
    }
    if tool not in tool_map:
        typer.echo(
            f"Error: Unknown tool '{tool}'. Available tools: {', '.join(tool_map.keys())}"
        )
        raise typer.Exit(1)
    tool_map[tool].install()
