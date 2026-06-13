import shutil
from devpack.utils.logger import get_logger
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

logger = get_logger(__name__)


def validate_tool(tool_name: str, tool_instance) -> bool:
    """Validate a single tool installation."""
    is_installed = tool_instance.is_installed()
    binary_path = tool_instance.get_binary_path()

    if is_installed:
        logger.info(f"[green]+[/green] {tool_name} is installed at {binary_path}")
        # Also check if it's in PATH
        if shutil.which(tool_name):
            logger.info(f"[green]+[/green] {tool_name} is in PATH")
            is_in_path = True
        else:
            logger.warning(
                f"[yellow]![/yellow] {tool_name} is installed but not in PATH"
            )
            is_in_path = False
    else:
        logger.warning(f"[-] {tool_name} is not installed")
        is_in_path = False

    return is_installed and is_in_path


def validate_all() -> None:
    """Validate all known tools."""
    logger.info("Validating DevToolPack installation...")

    tools = [
        ("terraform", TerraformTool()),
        ("awscli", AWSCLITool()),
        ("kubectl", KubectlTool()),
        ("git", GitTool()),
        ("sam", SamTool()),
        ("localstack", LocalStackTool()),
        ("cdk", CDKTool()),
        ("docker", DockerTool()),
        ("rust", RustTool()),
        ("golang", GolangTool()),
    ]

    all_valid = True
    for tool_name, tool_instance in tools:
        if not validate_tool(tool_name, tool_instance):
            all_valid = False

    if all_valid:
        logger.info("[green]+ All tools are properly installed![/green]")
    else:
        logger.warning(
            "[yellow]! Some tools are missing or not properly installed.[/yellow]"
        )
        logger.info("Run 'devpack install <tool>' to install missing tools.")
