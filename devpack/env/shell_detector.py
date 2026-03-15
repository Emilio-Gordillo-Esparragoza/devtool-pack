import os
import platform
from pathlib import Path
from typing import Optional


def detect_shell() -> str:
    """Detect the current shell."""
    shell = os.environ.get("SHELL", "")
    if shell:
        # Extract the shell name from the path
        return Path(shell).name

    # On Windows, SHELL might not be set, so we check COMSPEC or default to cmd
    if platform.system() == "Windows":
        comspec = os.environ.get("COMSPEC", "")
        if comspec:
            return Path(comspec).name.lower()
        return "cmd.exe"

    # Default to sh if we can't detect
    return "sh"


def get_shell_rc_path(shell: str) -> Optional[Path]:
    """Get the path to the shell's rc file."""
    home = Path.home()

    # Normalize shell name
    shell = shell.lower()

    if shell in ("bash",):
        return home / ".bashrc"
    elif shell in ("zsh",):
        return home / ".zshrc"
    elif shell in ("fish",):
        return home / ".config/fish/config.fish"
    elif shell in ("cmd.exe",):
        # Windows CMD doesn't have a standard rc file, but we can use %USERPROFILE%\autorun.bat
        return home / "autorun.bat"
    elif shell in ("powershell.exe", "pwsh"):
        # PowerShell profile
        if platform.system() == "Windows":
            return (
                home / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
            )
        else:
            return home / ".config" / "powershell" / "Microsoft.PowerShell_profile.ps1"
    else:
        # For unknown shells, we try to use a generic .shrc
        return home / f".{shell}rc"
