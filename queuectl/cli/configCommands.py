import typer
from queuectl.config import ConfigRepo

configApp = typer.Typer(help="Manage configuration values")
configRepo = ConfigRepo()

@configApp.command("set")
def setConfi(key: str, value: str):
    configRepo.setConfig(key, value)
    typer.echo(f"Config '{key} set to {value}")

@configApp.command("get")
def getConfig(key: str):
    val = configRepo.getConfig(key)
    if val is None:
        typer.echo(f"Config '{key} not found")
    else:
        typer.echo(f"{key} = {val}")

@configApp.command("list")
def listConfig():
    configs = configRepo.getAll()
    if not configs:
        typer.echo("No configuration found")
        return

    typer.echo("Current configuration:")
    for key, value in configs.items():
        typer.echo(f"{key}:{value}")
