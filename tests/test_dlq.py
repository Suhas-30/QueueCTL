import pytest
import uuid
from queuectl.dbConnection import getConnection

def testDlqJobstate():
    job_id = str(uuid.uuid4())
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO jobs (id, command, state, attempts, max_retries, created_at, updated_at)
            VALUES (?, 'echo fail', 'dead', 3, 3, datetime('now'), datetime('now'))
        """, (job_id,))
        conn.commit()

    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cur.fetchone()
        assert row is not None
        assert row["state"] == "dead"