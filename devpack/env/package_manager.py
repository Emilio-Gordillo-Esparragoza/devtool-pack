"""Cross-platform package manager detection and operations."""

import platform
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Literal, Dict, List


PackageManagerType = Literal[
    "apt", "pacman", "dnf", "yum", "brew", "choco", "winget", "none"
]


class PackageManager:
    """Detect and use system package managers across platforms."""

    def __init__(self):
        self._detected: Optional[PackageManagerType] = None
        self._distro_info: Optional[Dict[str, str]] = None

    def detect(self) -> PackageManagerType:
        """Detect the available package manager for the current system."""
        if self._detected is not None:
            return self._detected

        system = platform.system().lower()

        if system == "windows":
            if shutil.which("winget"):
                self._detected = "winget"
            elif shutil.which("choco"):
                self._detected = "choco"
            else:
                self._detected = "none"
            return self._detected

        if system == "darwin":
            if shutil.which("brew"):
                self._detected = "brew"
            else:
                self._detected = "none"
            return self._detected

        # Linux - check distro
        self._distro_info = self._read_os_release()
        distro_id = self._distro_info.get("ID", "").lower()
        distro_like = self._distro_info.get("ID_LIKE", "").lower()

        # Arch-based (cachyos, arch, manjaro, endeavour, etc.)
        if (
            distro_id in ("arch", "cachyos", "manjaro", "endeavouros")
            or "arch" in distro_like
        ):
            if shutil.which("pacman"):
                self._detected = "pacman"
                return self._detected

        # Debian/Ubuntu-based
        if (
            distro_id in ("debian", "ubuntu", "linuxmint", "pop", "elementary", "kali")
            or "debian" in distro_like
            or "ubuntu" in distro_like
        ):
            if shutil.which("apt"):
                self._detected = "apt"
                return self._detected

        # Fedora/RHEL-based
        if (
            distro_id in ("fedora", "rhel", "centos", "rocky", "almalinux", "nobara")
            or "fedora" in distro_like
            or "rhel" in distro_like
        ):
            if shutil.which("dnf"):
                self._detected = "dnf"
            elif shutil.which("yum"):
                self._detected = "yum"
            else:
                self._detected = "none"
            return self._detected

        # Fallback: check available managers
        for pm in ("pacman", "apt", "dnf", "yum"):
            if shutil.which(pm):
                self._detected = pm
                return self._detected

        self._detected = "none"
        return self._detected

    def _read_os_release(self) -> Dict[str, str]:
        """Parse /etc/os-release for distro information."""
        info = {}
        os_release = Path("/etc/os-release")
        if os_release.exists():
            for line in os_release.read_text().splitlines():
                if "=" in line:
                    key, value = line.split("=", 1)
                    info[key] = value.strip('"')
        return info

    def get_distro_info(self) -> Dict[str, str]:
        """Get cached distro info, detecting if needed."""
        if self._distro_info is None:
            self.detect()
        return self._distro_info or {}

    def is_arch_based(self) -> bool:
        """Check if running on Arch-based distribution."""
        info = self.get_distro_info()
        distro_id = info.get("ID", "").lower()
        distro_like = info.get("ID_LIKE", "").lower()
        return (
            distro_id in ("arch", "cachyos", "manjaro", "endeavouros")
            or "arch" in distro_like
        )

    def is_debian_based(self) -> bool:
        """Check if running on Debian/Ubuntu-based distribution."""
        info = self.get_distro_info()
        distro_id = info.get("ID", "").lower()
        distro_like = info.get("ID_LIKE", "").lower()
        return (
            distro_id in ("debian", "ubuntu", "linuxmint", "pop", "elementary", "kali")
            or "debian" in distro_like
            or "ubuntu" in distro_like
        )

    def is_fedora_based(self) -> bool:
        """Check if running on Fedora/RHEL-based distribution."""
        info = self.get_distro_info()
        distro_id = info.get("ID", "").lower()
        distro_like = info.get("ID_LIKE", "").lower()
        return (
            distro_id in ("fedora", "rhel", "centos", "rocky", "almalinux", "nobara")
            or "fedora" in distro_like
            or "rhel" in distro_like
        )

    def install(
        self,
        packages: List[str],
        package_map: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> bool:
        """Install packages using the detected package manager.

        Args:
            packages: List of generic package names
            package_map: Optional mapping from generic name to manager-specific name
                       e.g., {"terraform": {"apt": "terraform", "pacman": "terraform"}}

        Returns:
            True if installation succeeded, False otherwise
        """
        pm = self.detect()
        if pm == "none":
            return False

        # Resolve package names for this manager
        resolved = []
        for pkg in packages:
            if package_map and pkg in package_map:
                pm_specific = package_map[pkg].get(pm)
                if pm_specific:
                    resolved.append(pm_specific)
                else:
                    resolved.append(pkg)  # fallback to generic name
            else:
                resolved.append(pkg)

        try:
            if pm == "apt":
                subprocess.run(
                    ["sudo", "apt", "update"], check=True, capture_output=True
                )
                subprocess.run(["sudo", "apt", "install", "-y", *resolved], check=True)
            elif pm == "pacman":
                subprocess.run(
                    ["sudo", "pacman", "-Sy", "--noconfirm", *resolved], check=True
                )
            elif pm == "dnf":
                subprocess.run(["sudo", "dnf", "install", "-y", *resolved], check=True)
            elif pm == "yum":
                subprocess.run(["sudo", "yum", "install", "-y", *resolved], check=True)
            elif pm == "brew":
                subprocess.run(["brew", "install", *resolved], check=True)
            elif pm == "choco":
                subprocess.run(["choco", "install", "-y", *resolved], check=True)
            elif pm == "winget":
                for pkg in resolved:
                    subprocess.run(
                        [
                            "winget",
                            "install",
                            "--id",
                            pkg,
                            "--silent",
                            "--accept-source-agreements",
                            "--accept-package-agreements",
                        ],
                        check=True,
                    )
            else:
                return False
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, PermissionError):
            return False

    def is_installed(
        self, package: str, package_map: Optional[Dict[str, Dict[str, str]]] = None
    ) -> bool:
        """Check if a package is installed via package manager."""
        pm = self.detect()
        if pm == "none":
            return False

        # Resolve package name
        resolved = package
        if package_map and package in package_map:
            pm_specific = package_map[package].get(pm)
            if pm_specific:
                resolved = pm_specific

        try:
            if pm == "apt":
                result = subprocess.run(["dpkg", "-l", resolved], capture_output=True)
                return result.returncode == 0
            elif pm == "pacman":
                result = subprocess.run(["pacman", "-Q", resolved], capture_output=True)
                return result.returncode == 0
            elif pm in ("dnf", "yum"):
                result = subprocess.run(["rpm", "-q", resolved], capture_output=True)
                return result.returncode == 0
            elif pm == "brew":
                result = subprocess.run(
                    ["brew", "list", "--formula", resolved], capture_output=True
                )
                return result.returncode == 0
            elif pm == "choco":
                result = subprocess.run(
                    ["choco", "list", "--local-only", resolved], capture_output=True
                )
                return result.returncode == 0
            elif pm == "winget":
                result = subprocess.run(
                    ["winget", "list", "--id", resolved], capture_output=True
                )
                return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return False


# Global instance
_package_manager: Optional[PackageManager] = None


def get_package_manager() -> PackageManager:
    """Get the global package manager instance."""
    global _package_manager
    if _package_manager is None:
        _package_manager = PackageManager()
    return _package_manager
