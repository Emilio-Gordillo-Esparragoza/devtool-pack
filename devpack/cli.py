import typer
from devpack.commands import install, doctor, list_

app = typer.Typer(help="DevToolPack: CLI for DevOps tools installation")

app.command()(install.install)
app.command()(doctor.doctor)
app.command()(list_.list_tools)


def main():
    app()


if __name__ == "__main__":
    main()
