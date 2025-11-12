import typer
from queuectl.worker.manager import startWorkers

workerApp = typer.Typer(help="Manage worker processes (start, stop, etc.)")

@workerApp.command("start")
def start(count: int = typer.Option(1, help="Number of workers to start")):
    startWorkers(count)