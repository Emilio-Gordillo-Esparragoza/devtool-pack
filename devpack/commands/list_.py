import typer


def list_tools():
    """List available tools."""
    tools = [
        "terraform",
        "awscli",
        "kubectl",
        "git",
        "sam",
        "localstack",
        "cdk",
        "docker",
        "rust",
        "golang",
        "node",
    ]
    typer.echo("Available tools:")
    for tool in tools:
        typer.echo(f"  - {tool}")
