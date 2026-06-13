from pathlib import Path
from unittest.mock import patch, MagicMock

from devpack.tools.rust import RustTool


def test_rust_tool_initialization():
    tool = RustTool()
    assert tool.name == "rustc"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_rust_download_url_windows():
    with patch("devpack.tools.base_tool._current_os", return_value="windows"):
        tool = RustTool()
        assert "rustup-init" in tool.download_url
        assert "windows" in tool.download_url


def test_rust_download_url_linux():
    with patch("devpack.tools.base_tool._current_os", return_value="linux"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = RustTool()
        assert "rustup-init" in tool.download_url
        assert "linux" in tool.download_url


def test_rust_download_url_darwin():
    with patch("devpack.tools.base_tool._current_os", return_value="darwin"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = RustTool()
        assert "rustup-init" in tool.download_url
        assert "darwin" in tool.download_url


@patch("devpack.tools.rust.shutil.which")
def test_rust_tool_is_installed_false(mock_which):
    mock_which.return_value = None
    tool = RustTool()
    assert not tool.is_installed()


@patch("devpack.tools.rust.shutil.which")
def test_rust_tool_is_installed_true(mock_which):
    mock_which.return_value = "/usr/local/bin/rustc"
    tool = RustTool()
    assert tool.is_installed()


@patch("devpack.tools.rust.download_file")
@patch("devpack.tools.rust.subprocess")
@patch("devpack.tools.rust.add_to_path")
@patch("devpack.tools.rust.Path")
@patch("devpack.tools.rust.os")
def test_rust_tool_install(
    mock_os, mock_path_class, mock_add_to_path, mock_subprocess, mock_download_file
):
    mock_os.name = "nt"
    mock_rustup_init = MagicMock()
    mock_download_file.return_value = mock_rustup_init
    mock_cargo_bin = MagicMock()
    mock_cargo_bin.exists.return_value = True
    mock_path_class.return_value = mock_cargo_bin

    tool = RustTool()
    fake_url = "https://static.rust-lang.org/rustup/dist/i686-pc-windows-gnu/rustup-init.exe"
    with patch.object(tool, "is_installed", return_value=False), \
         patch.object(type(tool), "download_url", new_callable=lambda: property(lambda self: fake_url)):
        tool.install()

    mock_download_file.assert_called_once()
    mock_subprocess.run.assert_called_once_with(
        [str(mock_rustup_init), "-y"], check=True
    )
    mock_add_to_path.assert_called_once()
