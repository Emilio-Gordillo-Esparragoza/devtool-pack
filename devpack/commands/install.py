import typer
from devpack.tools.terraform import TerraformTool
from devpack.tools.awscli import AWSCLITool
from devpack.tools.kubectl import KubectlTool
from devpack.tools.git import GitTool
from devpack.tools.sam import SamTool
from devpack.tools.localstack import LocalStackTool
from devpack.tools.cdk import CDKTool
from devpack.tools.docker import DockerTool
from devpack.tools.rust import RustTool
from devpack.tools.golang import GolangTool


def install(
    tool: str = typer.Argument(
        ...,
        help="Tool to install (terraform, awscli, kubectl, git, sam, localstack, cdk, docker, rust, golang)",
    ),
):
    """Install a DevOps tool."""
    tool_map = {
        "terraform": TerraformTool(),
        "awscli": AWSCLITool(),
        "kubectl": KubectlTool(),
        "git": GitTool(),
        "sam": SamTool(),
        "localstack": LocalStackTool(),
        "cdk": CDKTool(),
        "docker": DockerTool(),
        "rust": RustTool(),
        "golang": GolangTool(),
    }
    if tool not in tool_map:
        typer.echo(
            f"Error: Unknown tool '{tool}'. Available tools: {', '.join(tool_map.keys())}"
        )
        raise typer.Exit(1)
    tool_map[tool].install()
