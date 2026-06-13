"""Tests for env.path_manager and env.shell_detector."""
import os
from pathlib import Path, PurePosixPath
from unittest.mock import patch

from devpack.env.path_manager import _get_path_export_line, add_to_path, remove_from_path
from devpack.env.shell_detector import detect_shell, get_shell_rc_path


# ---------------------------------------------------------------------------
# _get_path_export_line  (pure logic, no filesystem)
# ---------------------------------------------------------------------------

def test_export_line_bash():
    line = _get_path_export_line(PurePosixPath("/usr/local/bin"), "bash")
    assert line.startswith("export PATH=")
    assert "/usr/local/bin" in line


def test_export_line_zsh():
    line = _get_path_export_line(PurePosixPath("/usr/local/bin"), "zsh")
    assert "export PATH=" in line


def test_export_line_fish():
    line = _get_path_export_line(PurePosixPath("/usr/local/bin"), "fish")
    assert "fish_add_path" in line


def test_export_line_cmd():
    line = _get_path_export_line(PurePosixPath("C:/bin"), "cmd.exe")
    assert "set PATH=" in line


def test_export_line_powershell():
    line = _get_path_export_line(PurePosixPath("C:/bin"), "powershell.exe")
    assert "$env:PATH" in line


def test_export_line_unknown_shell():
    line = _get_path_export_line(PurePosixPath("/usr/local/bin"), "nushell")
    assert "export PATH=" in line  # fallback to bash-style


# ---------------------------------------------------------------------------
# add_to_path (unix rc-file path) — patch resolve to stay cross-platform
# ---------------------------------------------------------------------------

def _fake_resolve(path_obj):
    """Return the path unchanged, avoiding PosixPath instantiation on Windows."""
    return path_obj


def test_add_to_path_unix_new_entry(tmp_path):
    rc_file = tmp_path / ".bashrc"
    rc_file.write_text("# existing\n")
    target_dir = tmp_path / "bin"

    with patch("devpack.env.path_manager.os.name", "posix"), \
         patch("devpack.env.path_manager.detect_shell", return_value="bash"), \
         patch("devpack.env.path_manager.get_shell_rc_path", return_value=rc_file), \
         patch("devpack.env.path_manager.Path.resolve", _fake_resolve), \
         patch.dict(os.environ, {"PATH": "/usr/bin"}, clear=False):
        add_to_path(str(target_dir))

    content = rc_file.read_text()
    assert str(target_dir) in content
    assert "Added by devtoolpack" in content


def test_add_to_path_unix_already_present(tmp_path):
    target_dir = tmp_path / "bin"
    rc_file = tmp_path / ".bashrc"
    rc_file.write_text(f'export PATH="{target_dir}:$PATH"\n')

    with patch("devpack.env.path_manager.os.name", "posix"), \
         patch("devpack.env.path_manager.detect_shell", return_value="bash"), \
         patch("devpack.env.path_manager.get_shell_rc_path", return_value=rc_file), \
         patch("devpack.env.path_manager.Path.resolve", _fake_resolve), \
         patch.dict(os.environ, {"PATH": str(target_dir)}, clear=False):
        add_to_path(str(target_dir))

    content = rc_file.read_text()
    assert content.count(str(target_dir)) == 1


def test_add_to_path_unix_creates_rc_file(tmp_path):
    rc_file = tmp_path / ".newrc"
    target_dir = tmp_path / "bin"

    with patch("devpack.env.path_manager.os.name", "posix"), \
         patch("devpack.env.path_manager.detect_shell", return_value="bash"), \
         patch("devpack.env.path_manager.get_shell_rc_path", return_value=rc_file), \
         patch("devpack.env.path_manager.Path.resolve", _fake_resolve), \
         patch.dict(os.environ, {"PATH": "/usr/bin"}, clear=False):
        add_to_path(str(target_dir))

    assert rc_file.exists()
    assert str(target_dir) in rc_file.read_text()


def test_add_to_path_none_rc_file(tmp_path):
    """When rc_file is None the function should return early without crashing."""
    fake_path = tmp_path / "bin"
    with patch("devpack.env.path_manager.os.name", "posix"), \
         patch("devpack.env.path_manager.detect_shell", return_value="unknown"), \
         patch("devpack.env.path_manager.get_shell_rc_path", return_value=None), \
         patch("devpack.env.path_manager.Path.resolve", _fake_resolve):
        add_to_path(str(fake_path))  # should not raise


# ---------------------------------------------------------------------------
# remove_from_path
# ---------------------------------------------------------------------------

def test_remove_from_path_removes_entry(tmp_path):
    target_dir = tmp_path / "bin"
    rc_file = tmp_path / ".bashrc"
    rc_file.write_text(
        f"# Added by devtoolpack\nexport PATH=\"{target_dir}:$PATH\"\n# other line\n"
    )

    with patch("devpack.env.path_manager.os.name", "posix"), \
         patch("devpack.env.path_manager.detect_shell", return_value="bash"), \
         patch("devpack.env.path_manager.get_shell_rc_path", return_value=rc_file), \
         patch("devpack.env.path_manager.Path.resolve", _fake_resolve):
        remove_from_path(str(target_dir))

    content = rc_file.read_text()
    assert "Added by devtoolpack" not in content


def test_remove_from_path_missing_rc_file(tmp_path):
    """Should return early when rc file does not exist."""
    rc_file = tmp_path / ".nonexistent"
    fake_path = tmp_path / "bin"
    with patch("devpack.env.path_manager.os.name", "posix"), \
         patch("devpack.env.path_manager.detect_shell", return_value="bash"), \
         patch("devpack.env.path_manager.get_shell_rc_path", return_value=rc_file), \
         patch("devpack.env.path_manager.Path.resolve", _fake_resolve):
        remove_from_path(str(fake_path))  # should not raise


# ---------------------------------------------------------------------------
# shell_detector
# ---------------------------------------------------------------------------

def test_detect_shell_from_env():
    with patch.dict(os.environ, {"SHELL": "/bin/zsh"}, clear=False):
        assert detect_shell() == "zsh"


def test_detect_shell_windows_comspec():
    with patch.dict(
        os.environ,
        {"COMSPEC": "C:\\Windows\\System32\\cmd.exe"},
        clear=True,  # wipe SHELL so the Windows branch is reached
    ), patch("devpack.env.shell_detector.platform.system", return_value="Windows"):
        assert detect_shell() == "cmd.exe"


def test_detect_shell_default():
    with patch.dict(os.environ, {"SHELL": ""}, clear=False), \
         patch("devpack.env.shell_detector.platform.system", return_value="Linux"):
        assert detect_shell() == "sh"


def test_get_shell_rc_bash():
    assert get_shell_rc_path("bash") == Path.home() / ".bashrc"


def test_get_shell_rc_zsh():
    assert get_shell_rc_path("zsh") == Path.home() / ".zshrc"


def test_get_shell_rc_fish():
    assert get_shell_rc_path("fish") == Path.home() / ".config/fish/config.fish"


def test_get_shell_rc_powershell_linux():
    with patch("devpack.env.shell_detector.platform.system", return_value="Linux"):
        rc = get_shell_rc_path("powershell.exe")
    assert "Microsoft.PowerShell_profile.ps1" in str(rc)


def test_get_shell_rc_unknown():
    rc = get_shell_rc_path("nushell")
    assert ".nushellrc" in str(rc)
