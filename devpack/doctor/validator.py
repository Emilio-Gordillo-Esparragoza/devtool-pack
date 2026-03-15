import shutil
from devpack.utils.logger import get_logger
from devpack.tools.terraform import TerraformTool
from devpack.tools.awscli import AWSCLITool
from devpack.tools.kubectl import KubectlTool

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
        else:
            logger.warning(
                f"[yellow]![/yellow] {tool_name} is installed but not in PATH"
            )
    else:
        logger.warning(f"[-] {tool_name} is not installed")

    return is_installed


def validate_all() -> None:
    """Validate all known tools."""
    logger.info("Validating DevToolPack installation...")

    tools = [
        ("terraform", TerraformTool()),
        ("awscli", AWSCLITool()),
        ("kubectl", KubectlTool()),
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
