import os
from pathlib import Path
from devpack.utils.logger import get_logger
from devpack.env.shell_detector import detect_shell, get_shell_rc_path

logger = get_logger(__name__)


def _get_path_export_line(dir_path: Path, shell: str) -> str:
    """Get the line to export PATH for a given shell."""
    dir_str = str(dir_path)
    if shell in ("bash", "zsh"):
        return f'export PATH="{dir_str}:$PATH"'
    elif shell == "fish":
        return f'fish_add_path "{dir_str}"'
    elif shell in ("cmd.exe",):
        return f'set PATH="{dir_str};%PATH%"'
    elif shell in ("powershell.exe", "pwsh"):
        return f'$env:PATH = "{dir_str};$env:PATH"'
    else:
        # Fallback to bash-style
        return f'export PATH="{dir_str}:$PATH"'


def add_to_path(directory: str) -> None:
    """Add a directory to the PATH environment variable for the current shell."""
    # Convert to Path and resolve to absolute path
    dir_path = Path(directory).resolve()

    # Get the current shell and its rc file
    shell = detect_shell()
    rc_file = get_shell_rc_path(shell)

    if rc_file is None:
        logger.warning(f"Could not determine rc file for shell: {shell}")
        return

    # Check if the directory is already in PATH in the rc file
    path_line = _get_path_export_line(dir_path, shell)
    if rc_file.exists():
        content = rc_file.read_text()
        if str(dir_path) in content:
            logger.info(f"{dir_path} is already in PATH in {rc_file}")
            return

    # Append the export line to the rc file
    with rc_file.open("a") as f:
        f.write(f"\n# Added by devtoolpack\n{path_line}\n")

    logger.info(f"Added {dir_path} to PATH in {rc_file}")

    # Also update the current session's PATH (for immediate use)
    current_path = os.environ.get("PATH", "")
    if str(dir_path) not in current_path:
        if os.name == "nt":
            os.environ["PATH"] = f"{dir_path};{current_path}"
        else:
            os.environ["PATH"] = f"{dir_path}:{current_path}"


def remove_from_path(directory: str) -> None:
    """Remove a directory from the PATH environment variable in the shell rc file."""
    dir_path = Path(directory).resolve()
    shell = detect_shell()
    rc_file = get_shell_rc_path(shell)

    if rc_file is None or not rc_file.exists():
        logger.warning(f"Could not determine rc file for shell: {shell}")
        return

    # Read the file and remove any line that adds the directory to PATH
    lines = rc_file.read_text().splitlines()
    new_lines = []
    for line in lines:
        # Remove the line if it's the devtoolpack added line or contains our specific addition
        if "# Added by devtoolpack" in line:
            # Skip the comment line and the next line (the actual PATH line)
            continue
        # Also remove any line that looks like it's setting PATH and contains our dir_path
        # This is a fallback in case the format is different
        if str(dir_path) in line and ("PATH" in line or "path" in line):
            # Check if it's a line we added (by checking for the dir_path and PATH keyword)
            # We'll be conservative and only remove if it's likely our line
            continue
        new_lines.append(line)

    # Write back the file
    rc_file.write_text("\n".join(new_lines))
    logger.info(f"Removed {dir_path} from PATH in {rc_file}")
