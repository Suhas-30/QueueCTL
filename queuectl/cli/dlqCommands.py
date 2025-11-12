import typer
from rich.table import Table
from rich.console import Console
from queuectl.dbConnection import getConnection

dlqApp = typer.Typer(help="Manage Dead Letter Queue (DLQ)")
console = Console()

@dlqApp.command("list")
def listDlq():
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM jobs WHERE state = 'dead'")
        rows = cur.fetchall()
    
    if not rows:
        console.print("No jobs found in DLQ")
        return
    
    
    table = Table(title="Dead Letter Queue (DLQ)")
    table.add_column("ID", style="cyan")
    table.add_column("Command", style="magenta")
    table.add_column("Attempts", justify="right")
    table.add_column("Last Error", style="red")
    
    for row in rows:
        table.add_row(row["id"], row["command"], str(row["attempts"]), row["last_error"] or "-")
    
    console.print(table)
    
@dlqApp.command("retry")
def retryDlq(job_id: str):
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM jobs WHERE id = ? AND state = 'dead'", (job_id,))
        job = cur.fetchone()

        if not job:
            console.print(f"No DLQ job found with ID {job_id}")
            return

        cur.execute("""
            UPDATE jobs
            SET state = 'pending',
                attempts = 0,
                last_error = NULL,
                next_retry_at = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (job_id,))
        conn.commit()

    console.print(f"Job {job_id} moved back to pending queue.")
    