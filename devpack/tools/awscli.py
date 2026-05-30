import os
import platform
import subprocess
from pathlib import Path
from devpack.tools.base_tool import BaseTool
from devpack.installer.downloader import download_file
from devpack.env.path_manager import add_to_path


class AWSCLITool(BaseTool):
    """AWS CLI tool installer."""

    def __init__(self):
        super().__init__("aws")

    @property
    def download_url(self) -> str:
        # AWS CLI v2 for Windows
        return "https://awscli.amazonaws.com/AWSCLIV2.msi"

    def install(self) -> None:
        if self.is_installed():
            print(f"{self.name} is already installed.")
            return

        print(f"Downloading {self.name}...")
        msi_path = download_file(self.download_url, self.bin_dir)

        if os.name == "nt":
            # Install MSI silently to a subdirectory
            install_dir = self.bin_dir / "aws-cli"
            install_dir.mkdir(parents=True, exist_ok=True)
            try:
                # msiexec /i <msi> /qn TARGETDIR=<install_dir>
                cmd = [
                    "msiexec",
                    "/i",
                    str(msi_path),
                    "/qn",
                    f"TARGETDIR={install_dir}",
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                # The installed aws.exe is typically under install_dir/aws
                installed_bin = install_dir / "aws"
                if installed_bin.is_dir():
                    aws_exe = installed_bin / "bin" / "aws.exe"
                    # Ensure the bin directory exists
                    aws_exe.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # Fallback: maybe directly in install_dir
                    aws_exe = install_dir / "aws.exe"
                if aws_exe.is_file():
                    # Copy or move the aws.exe to our bin directory for consistency
                    target_exe = self.bin_dir / "aws.exe"
                    # Avoid overwriting if same
                    if aws_exe.resolve() != target_exe.resolve():
                        # Copy file
                        import shutil

                        shutil.copy2(aws_exe, target_exe)
                    # Ensure executable (though .exe doesn't need chmod)
                    # Add the bin directory of the installed aws to PATH
                    # We'll add the directory containing aws.exe (i.e., installed_bin/bin) to PATH
                    aws_bin_dir = installed_bin / "bin"
                    if aws_bin_dir.is_dir():
                        add_to_path(str(aws_bin_dir))
                    else:
                        # Fallback: add install_dir
                        add_to_path(str(install_dir))
                    print(f"{self.name} installed successfully.")
                else:
                    print(
                        f"Could not find aws.exe after installation. Expected at {aws_exe}"
                    )
                    # Clean up
                    msi_path.unlink()
                    raise RuntimeError("AWS CLI installation failed: aws.exe not found")
            except subprocess.CalledProcessError as e:
                print(f"MSI installation failed: {e}")
                # Clean up
                msi_path.unlink()
                raise
            except Exception as e:
                print(f"Error during AWS CLI installation: {e}")
                # Clean up
                msi_path.unlink()
                raise
            finally:
                # Remove the downloaded MSI
                try:
                    msi_path.unlink()
                except OSError:
                    pass
        else:
            # For Unix-like systems, we'd use the bundled installer
            print(
                f"{self.name} installation on {os.name} not fully implemented in this demo."
            )
