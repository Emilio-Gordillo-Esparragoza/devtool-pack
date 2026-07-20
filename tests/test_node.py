"""Tests for the Node.js tool installer."""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from devpack.tools.node import NodeTool


def test_node_tool_initialization():
    tool = NodeTool()
    assert tool.name == "node"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_node_download_url_linux():
    with patch("devpack.tools.base_tool._current_os", return_value="linux"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = NodeTool()
        assert "node" in tool.download_url
        assert "linux" in tool.download_url


def test_node_download_url_windows():
    with patch("devpack.tools.base_tool._current_os", return_value="windows"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = NodeTool()
        assert "win" in tool.download_url


def test_node_download_url_darwin():
    with patch("devpack.tools.base_tool._current_os", return_value="darwin"), \
         patch("devpack.tools.base_tool._current_arch", return_value="arm64"):
        tool = NodeTool()
        assert "darwin" in tool.download_url


@patch("devpack.tools.node.shutil.which")
def test_node_is_installed_false(mock_which):
    mock_which.return_value = None
    tool = NodeTool()
    with patch.object(tool, "_is_installed_via_package_manager", return_value=False):
        assert not tool.is_installed()


@patch("devpack.tools.node.shutil.which")
def test_node_is_installed_true(mock_which):
    mock_which.return_value = "/usr/bin/node"
    tool = NodeTool()
    assert tool.is_installed()


@patch("devpack.tools.node.shutil.which")
def test_node_get_binary_path_from_which(mock_which):
    mock_which.return_value = "/usr/local/bin/node"
    tool = NodeTool()
    assert tool.get_binary_path() == Path("/usr/local/bin/node")


@patch("devpack.tools.node.shutil.which")
def test_node_get_binary_path_fallback(mock_which):
    mock_which.return_value = None
    tool = NodeTool()
    assert tool.get_binary_path() == tool.bin_dir / "node"


def test_node_install_already_installed(capsys):
    tool = NodeTool()
    with patch.object(tool, "is_installed", return_value=True):
        tool.install()
    assert "already installed" in capsys.readouterr().out


def test_node_install_via_package_manager(capsys):
    tool = NodeTool()
    with patch.object(tool, "is_installed", return_value=False), \
         patch.object(tool, "_install_via_package_manager", return_value=True):
        tool.install()
    assert "installed successfully" in capsys.readouterr().out


def test_node_install_no_url():
    tool = NodeTool()
    with patch.object(tool, "is_installed", return_value=False), \
         patch.object(tool, "_install_via_package_manager", return_value=False), \
         patch.object(
             type(tool),
             "download_url",
             new_callable=lambda: property(lambda self: ""),
         ):
        with pytest.raises(RuntimeError, match="Node.js"):
            tool.install()


@patch("devpack.tools.node.download_file")
@patch("devpack.tools.node.extract_archive")
@patch("devpack.tools.node.add_to_path")
@patch("devpack.tools.node.os")
def test_node_install_download_unix(
    mock_os, mock_add_to_path, mock_extract, mock_download, tmp_path
):
    mock_os.name = "posix"
    mock_os.chmod = MagicMock()
    mock_os.access = MagicMock(return_value=True)

    archive = tmp_path / "node.tar.xz"
    archive.write_text("x")
    mock_download.return_value = archive

    extracted = tmp_path / "extracted"
    bin_dir = extracted / "bin"
    bin_dir.mkdir(parents=True)
    node_binary = bin_dir / "node"
    node_binary.write_text("#!/bin/sh\n")
    mock_extract.return_value = extracted

    tool = NodeTool()
    tool.bin_dir = tmp_path / "bin"
    tool.bin_dir.mkdir()
    fake_url = "https://nodejs.org/dist/v20.11.0/node-v20.11.0-linux-x64.tar.xz"

    with patch.object(tool, "is_installed", return_value=False), \
         patch.object(tool, "_install_via_package_manager", return_value=False), \
         patch.object(
             type(tool),
             "download_url",
             new_callable=lambda: property(lambda self: fake_url),
         ):
        tool.install()

    mock_download.assert_called_once()
    mock_extract.assert_called_once()
    assert not archive.exists()
    assert (tool.bin_dir / "node").exists()
    mock_add_to_path.assert_called_once()


@patch("devpack.tools.node.download_file")
@patch("devpack.tools.node.extract_archive")
@patch("devpack.tools.node.add_to_path")
@patch("devpack.tools.node.os")
def test_node_install_download_windows_rglob(
    mock_os, mock_add_to_path, mock_extract, mock_download, tmp_path
):
    mock_os.name = "nt"

    archive = tmp_path / "node.zip"
    archive.write_text("x")
    mock_download.return_value = archive

    extracted = tmp_path / "extracted"
    nested = extracted / "node-v20" / "bin"
    nested.mkdir(parents=True)
    node_exe = nested / "node.exe"
    node_exe.write_text("bin")
    # Primary windows path does not exist; force rglob fallback for "node"
    mock_extract.return_value = extracted

    tool = NodeTool()
    tool.bin_dir = tmp_path / "bin"
    tool.bin_dir.mkdir()
    fake_url = "https://nodejs.org/dist/v20.11.0/node-v20.11.0-win-x64.zip"

    with patch.object(tool, "is_installed", return_value=False), \
         patch.object(tool, "_install_via_package_manager", return_value=False), \
         patch.object(
             type(tool),
             "download_url",
             new_callable=lambda: property(lambda self: fake_url),
         ), \
         patch("os.access", return_value=True):
        tool.install()

    mock_add_to_path.assert_called_once()
    assert not archive.exists()
