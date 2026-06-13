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


def _notify_environment_change():  # pragma: no cover
    """Notify the system that environment variables have changed (Windows only)."""
    if os.name == "nt":
        try:
            import ctypes

            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            SMTO_ABORTIFHUNG = 0x0002
            result = ctypes.c_long()
            SendMessageTimeoutW = ctypes.windll.user32.SendMessageTimeoutW
            SendMessageTimeoutW(
                HWND_BROADCAST,
                WM_SETTINGCHANGE,
                0,
                "Environment",
                SMTO_ABORTIFHUNG,
                5000,
                ctypes.byref(result),
            )
        except Exception as e:
            logger.warning(f"Could not notify environment change: {e}")


def add_to_path(directory: str) -> None:
    """Add a directory to the PATH environment variable permanently."""
    # Convert to Path and resolve to absolute path
    dir_path = Path(directory).resolve()

    # Get the current shell and its rc file
    shell = detect_shell()
    rc_file = get_shell_rc_path(shell)

    if rc_file is None:
        logger.warning(f"Could not determine rc file for shell: {shell}")
        return

    # Persist PATH based on platform
    if os.name == "nt":  # pragma: no cover
        # Windows: Update registry
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS
            ) as key:
                current_path, _ = winreg.QueryValueEx(key, "Path")
                paths = [p.strip() for p in current_path.split(";") if p.strip()]
                if str(dir_path) not in paths:
                    paths.append(str(dir_path))
                    new_path = ";".join(paths)
                    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                    logger.info(f"Added {dir_path} to PATH in registry")
                    # Notify system of environment change
                    _notify_environment_change()
                else:
                    logger.info(f"{dir_path} is already in PATH in registry")
        except Exception as e:
            logger.warning(f"Failed to update registry PATH: {e}")
            # Fallback to rc file method
            if rc_file is not None:
                path_line = _get_path_export_line(dir_path, shell)
                if rc_file.exists():
                    content = rc_file.read_text()
                    if str(dir_path) not in content:
                        with rc_file.open("a") as f:
                            f.write(f"\n# Added by devtoolpack\n{path_line}\n")
                        logger.info(f"Added {dir_path} to PATH in {rc_file} (fallback)")
                    else:
                        logger.info(
                            f"{dir_path} is already in PATH in {rc_file} (fallback)"
                        )
                else:
                    with rc_file.open("w") as f:
                        f.write(f"# Added by devtoolpack\n{path_line}\n")
                    logger.info(f"Created {rc_file} and added {dir_path} to PATH")
    else:
        # Unix-like: Update shell rc file
        path_line = _get_path_export_line(dir_path, shell)
        if rc_file.exists():
            content = rc_file.read_text()
            if str(dir_path) not in content:
                with rc_file.open("a") as f:
                    f.write(f"\n# Added by devtoolpack\n{path_line}\n")
                logger.info(f"Added {dir_path} to PATH in {rc_file}")
            else:
                logger.info(f"{dir_path} is already in PATH in {rc_file}")
        else:
            with rc_file.open("w") as f:
                f.write(f"# Added by devtoolpack\n{path_line}\n")
            logger.info(f"Created {rc_file} and added {dir_path} to PATH")

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

    # Remove from registry on Windows
    if os.name == "nt":  # pragma: no cover
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS
            ) as key:
                current_path, _ = winreg.QueryValueEx(key, "Path")
                paths = [
                    p.strip()
                    for p in current_path.split(";")
                    if p.strip() and p.strip() != str(dir_path)
                ]
                new_path = ";".join(paths)
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                logger.info(f"Removed {dir_path} from PATH in registry")
                # Notify system of environment change
                _notify_environment_change()
        except Exception as e:
            logger.warning(f"Failed to update registry PATH: {e}")

    # Read the file and remove any line that adds the directory to PATH
    lines = rc_file.read_text().splitlines()
    new_lines = []
    skip_next = False
    for line in lines:
        if skip_next:
            skip_next = False
            continue
        # Remove the line if it's the devtoolpack added line or contains our specific addition
        if "# Added by devtoolpack" in line:
            # Skip the comment line and the next line (the actual PATH line)
            skip_next = True
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
