"""Tests for cross-platform package manager detection and operations."""
from unittest.mock import MagicMock, patch

from devpack.env.package_manager import PackageManager, get_package_manager


def test_detect_windows_winget():
    pm = PackageManager()
    with patch("platform.system", return_value="Windows"), \
         patch("shutil.which", side_effect=lambda c: c == "winget"):
        assert pm.detect() == "winget"


def test_detect_windows_choco():
    pm = PackageManager()
    with patch("platform.system", return_value="Windows"), \
         patch("shutil.which", side_effect=lambda c: c == "choco"):
        assert pm.detect() == "choco"


def test_detect_windows_none():
    pm = PackageManager()
    with patch("platform.system", return_value="Windows"), \
         patch("shutil.which", return_value=None):
        assert pm.detect() == "none"


def test_detect_darwin_brew():
    pm = PackageManager()
    with patch("platform.system", return_value="Darwin"), \
         patch("shutil.which", side_effect=lambda c: c == "brew"):
        assert pm.detect() == "brew"


def test_detect_darwin_none():
    pm = PackageManager()
    with patch("platform.system", return_value="Darwin"), \
         patch("shutil.which", return_value=None):
        assert pm.detect() == "none"


def test_detect_linux_apt():
    pm = PackageManager()
    with patch("platform.system", return_value="Linux"), \
         patch.object(PackageManager, "_read_os_release", return_value={"ID": "ubuntu"}), \
         patch("shutil.which", side_effect=lambda c: c == "apt"):
        assert pm.detect() == "apt"


def test_detect_linux_pacman_arch():
    pm = PackageManager()
    with patch("platform.system", return_value="Linux"), \
         patch.object(
             PackageManager, "_read_os_release", return_value={"ID": "cachyos", "ID_LIKE": "arch"}
         ), \
         patch("shutil.which", side_effect=lambda c: c == "pacman"):
        assert pm.detect() == "pacman"


def test_detect_linux_dnf():
    pm = PackageManager()
    with patch("platform.system", return_value="Linux"), \
         patch.object(PackageManager, "_read_os_release", return_value={"ID": "fedora"}), \
         patch("shutil.which", side_effect=lambda c: c == "dnf"):
        assert pm.detect() == "dnf"


def test_detect_linux_yum():
    pm = PackageManager()
    with patch("platform.system", return_value="Linux"), \
         patch.object(PackageManager, "_read_os_release", return_value={"ID": "centos"}), \
         patch("shutil.which", side_effect=lambda c: c == "yum"):
        assert pm.detect() == "yum"


def test_detect_linux_fedora_none():
    pm = PackageManager()
    with patch("platform.system", return_value="Linux"), \
         patch.object(PackageManager, "_read_os_release", return_value={"ID": "fedora"}), \
         patch("shutil.which", return_value=None):
        assert pm.detect() == "none"


def test_detect_linux_fallback_pacman():
    pm = PackageManager()
    with patch("platform.system", return_value="Linux"), \
         patch.object(PackageManager, "_read_os_release", return_value={"ID": "unknown"}), \
         patch("shutil.which", side_effect=lambda c: c == "pacman"):
        assert pm.detect() == "pacman"


def test_detect_linux_none():
    pm = PackageManager()
    with patch("platform.system", return_value="Linux"), \
         patch.object(PackageManager, "_read_os_release", return_value={"ID": "unknown"}), \
         patch("shutil.which", return_value=None):
        assert pm.detect() == "none"


def test_detect_cached():
    pm = PackageManager()
    pm._detected = "apt"
    assert pm.detect() == "apt"


def test_read_os_release(tmp_path):
    release = tmp_path / "os-release"
    release.write_text('ID="ubuntu"\nID_LIKE="debian"\n')

    class FakePath:
        def __init__(self, *_args, **_kwargs):
            pass

        def exists(self):
            return True

        def read_text(self):
            return release.read_text()

    with patch("devpack.env.package_manager.Path", FakePath):
        pm = PackageManager()
        assert pm._read_os_release() == {"ID": "ubuntu", "ID_LIKE": "debian"}


def test_distro_helpers():
    pm = PackageManager()
    pm._distro_info = {"ID": "arch", "ID_LIKE": ""}
    assert pm.is_arch_based() is True
    assert pm.is_debian_based() is False
    assert pm.is_fedora_based() is False

    pm._distro_info = {"ID": "ubuntu", "ID_LIKE": "debian"}
    assert pm.is_debian_based() is True
    assert pm.is_arch_based() is False

    pm._distro_info = {"ID": "rhel", "ID_LIKE": "fedora"}
    assert pm.is_fedora_based() is True


def test_get_distro_info_triggers_detect():
    pm = PackageManager()
    with patch.object(pm, "detect") as mock_detect:
        pm._distro_info = None
        info = pm.get_distro_info()
        mock_detect.assert_called_once()
        assert info == {}


def test_install_none_returns_false():
    pm = PackageManager()
    pm._detected = "none"
    assert pm.install(["kubectl"]) is False


def test_install_apt_with_package_map():
    pm = PackageManager()
    pm._detected = "apt"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        ok = pm.install(
            ["node"],
            {"node": {"apt": "nodejs", "brew": "node"}},
        )
    assert ok is True
    assert mock_run.call_count == 2
    assert mock_run.call_args_list[1][0][0] == ["sudo", "apt", "install", "-y", "nodejs"]


def test_install_pacman():
    pm = PackageManager()
    pm._detected = "pacman"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        assert pm.install(["rust"]) is True
    mock_run.assert_called_once()
    assert "pacman" in mock_run.call_args[0][0]


def test_install_dnf_yum_brew_choco():
    for manager, expected in (
        ("dnf", "dnf"),
        ("yum", "yum"),
        ("brew", "brew"),
        ("choco", "choco"),
    ):
        pm = PackageManager()
        pm._detected = manager
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert pm.install(["pkg"]) is True
            assert expected in mock_run.call_args[0][0]


def test_install_winget():
    pm = PackageManager()
    pm._detected = "winget"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        assert pm.install(["OpenJS.NodeJS"]) is True
    assert mock_run.call_args[0][0][0] == "winget"


def test_install_failure_returns_false():
    import subprocess

    pm = PackageManager()
    pm._detected = "apt"
    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "apt")):
        assert pm.install(["missing"]) is False


def test_is_installed_none():
    pm = PackageManager()
    pm._detected = "none"
    assert pm.is_installed("kubectl") is False


def test_is_installed_apt_with_map():
    pm = PackageManager()
    pm._detected = "apt"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        assert pm.is_installed("node", {"node": {"apt": "nodejs"}}) is True
    mock_run.assert_called_once_with(["dpkg", "-l", "nodejs"], capture_output=True)


def test_is_installed_other_managers():
    cases = (
        ("pacman", ["pacman", "-Q", "pkg"]),
        ("dnf", ["rpm", "-q", "pkg"]),
        ("yum", ["rpm", "-q", "pkg"]),
        ("brew", ["brew", "list", "--formula", "pkg"]),
        ("choco", ["choco", "list", "--local-only", "pkg"]),
        ("winget", ["winget", "list", "--id", "pkg"]),
    )
    for manager, expected_cmd in cases:
        pm = PackageManager()
        pm._detected = manager
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert pm.is_installed("pkg") is True
            mock_run.assert_called_once_with(expected_cmd, capture_output=True)


def test_is_installed_exception_returns_false():
    pm = PackageManager()
    pm._detected = "apt"
    with patch("subprocess.run", side_effect=FileNotFoundError):
        assert pm.is_installed("kubectl") is False


def test_get_package_manager_singleton():
    import devpack.env.package_manager as pm_mod

    pm_mod._package_manager = None
    first = get_package_manager()
    second = get_package_manager()
    assert first is second
    pm_mod._package_manager = None
