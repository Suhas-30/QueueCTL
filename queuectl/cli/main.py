import typer
from rich.console import Console
from queuectl.cli.configCommands import configApp
from queuectl.cli.dlqCommands import dlqApp
from queuectl.cli.jobCommands import registerJobCommands
from queuectl.cli.workerCommands import workerApp

app = typer.Typer()
console = Console()

app.add_typer(workerApp, name="worker")
app.add_typer(dlqApp, name="dlq")
app.add_typer(configApp, name="config")

registerJobCommands(app)

if __name__ == "__main__":
    app()