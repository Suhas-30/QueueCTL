import typer 
from rich.console import Console
from rich.table import Table
from queuectl.repository import JobRepository
from queuectl.dbConnection import getConnection

repo = JobRepository()
console = Console()

def registerJobCommands(app: typer.Typer):
    @app.command()
    def enqueue(command: str, max_retries: int = 3):
        job_id = repo.addJob(command, max_retries)
        console.print(f"Job added with ID: {job_id}")
    
    @app.command()
    def list(state: str = "pending"):
        with getConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs WHERE state = ?", (state,))
            rows = cursor.fetchall()

        if not rows:
            console.print(f"No jobs found with state {state}")
            return
        
        table = Table(title=f"Jobs ({state})")
        table.add_column("ID", style="cyan")
        table.add_column("Command", style="magenta")
        table.add_column("State", style="green")
        table.add_column("Attempts", justify="right")
        table.add_column("Max Retries", justify="right")
        table.add_column("Created At", style="dim")
        
        for row in rows:
            table.add_row(
                row["id"],
                row["command"],
                row["state"],
                str(row["attempts"]),
                str(row["max_retries"]),
                row["created_at"]
            )
        console.print(table)

            