import subprocess
import sys


def test_devpack_list_tools():
    """Test that devpack list-tools works."""
    result = subprocess.run(
        [sys.executable, "-m", "devpack", "list-tools"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "Available tools:" in result.stdout
    assert "terraform" in result.stdout
    assert "awscli" in result.stdout
    assert "kubectl" in result.stdout


def test_devpack_help():
    """Test that devpack --help works."""
    result = subprocess.run(
        [sys.executable, "-m", "devpack", "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "DevToolPack: CLI for DevOps tools installation" in result.stdout


if __name__ == "__main__":
    test_devpack_list_tools()
    test_devpack_help()
    print("All CLI tests passed!")
