from pathlib import Path
from unittest.mock import patch, MagicMock

from devpack.tools.kubectl import KubectlTool


def test_kubectl_tool_initialization():
    tool = KubectlTool()
    assert tool.name == "kubectl"
    assert tool.bin_dir == Path.home() / ".devpack" / "bin"


def test_kubectl_download_url_windows():
    with patch("devpack.tools.base_tool._current_os", return_value="windows"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = KubectlTool()
        assert "kubectl" in tool.download_url
        assert "windows" in tool.download_url


def test_kubectl_download_url_linux():
    with patch("devpack.tools.base_tool._current_os", return_value="linux"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = KubectlTool()
        assert "kubectl" in tool.download_url
        assert "linux" in tool.download_url


def test_kubectl_download_url_darwin():
    with patch("devpack.tools.base_tool._current_os", return_value="darwin"), \
         patch("devpack.tools.base_tool._current_arch", return_value="amd64"):
        tool = KubectlTool()
        assert "kubectl" in tool.download_url
        assert "darwin" in tool.download_url


def test_kubectl_is_installed_false():
    tool = KubectlTool()
    with patch.object(tool, "get_binary_path") as mock_path:
        mock_path.return_value = MagicMock(is_file=lambda: False)
        with patch("os.access", return_value=False):
            assert not tool.is_installed()


def test_kubectl_is_installed_true():
    tool = KubectlTool()
    with patch.object(tool, "get_binary_path") as mock_path:
        mock_binary = MagicMock()
        mock_binary.is_file.return_value = True
        mock_path.return_value = mock_binary
        with patch("os.access", return_value=True):
            assert tool.is_installed()


@patch("devpack.tools.kubectl.download_file")
@patch("devpack.tools.kubectl.add_to_path")
@patch("devpack.tools.kubectl.os")
def test_kubectl_install(mock_os, mock_add_to_path, mock_download_file):
    mock_os.name = "posix"
    mock_os.chmod = MagicMock()
    fake_binary = MagicMock()
    mock_download_file.return_value = fake_binary
    fake_url = "https://dl.k8s.io/release/v1.27.0/bin/linux/amd64/kubectl"

    tool = KubectlTool()
    with patch.object(tool, "is_installed", return_value=False), \
         patch.object(type(tool), "download_url", new_callable=lambda: property(lambda self: fake_url)):
        tool.install()

    mock_download_file.assert_called_once()
    mock_add_to_path.assert_called_once()


def test_kubectl_install_already_installed(capsys):
    tool = KubectlTool()
    with patch.object(tool, "is_installed", return_value=True):
        tool.install()
    assert "already installed" in capsys.readouterr().out


def test_kubectl_install_no_url():
    tool = KubectlTool()
    with patch.object(tool, "is_installed", return_value=False), \
         patch.object(type(tool), "download_url", new_callable=lambda: property(lambda self: "")):
        try:
            tool.install()
            assert False, "Expected RuntimeError"
        except RuntimeError as e:
            assert "kubectl" in str(e)
