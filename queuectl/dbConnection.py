import sqlite3
from pathlib import Path

DBDIR = Path(__file__).parent.parent / "data"
DBDIR.mkdir(exist_ok=True)
DBPATH = DBDIR/"queuectl.db"

def getConnection():
    connection = sqlite3.connect(DBPATH, isolation_level=None)
    connection.row_factory = sqlite3.Row
    return connection

def initializeDB():
    with getConnection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
                       
                       CREATE TABLE IF NOT EXISTS jobs (
                           id TEXT PRIMARY KEY,
                           command TEXT NOT NULL,
                           state TEXT NOT NULL,
                           attempts INTEGER DEFAULT 0,
                           max_retries INTEGER DEFAULT 3,
                           next_retry_at TEXT,
                           created_at TEXT NOT NULL,
                           updated_at TEXT NOT NULL,
                           last_error TEXT
                       )
                       
                       """)
        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS config (
                            key TEXT PRIMARY KEY,
                            value TEXT NOT NULL
                        )
                       """)
        connection.commit()
        



