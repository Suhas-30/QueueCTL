from datetime import datetime, timezone
from queuectl.dbConnection import getConnection

def pickJob():
    now_iso = datetime.now(timezone.utc).isoformat()
    with getConnection() as conn:
        cur = conn.cursor()
        try:
            conn.execute("BEGIN IMMEDIATE")
            cur.execute(""" 
                            SELECT * FROM jobs WHERE state = 'pending'
                            AND (next_retry_at IS NULL OR next_retry_at <= ?)
                            ORDER BY created_at ASC
                            LIMIT 1 
                        """, (now_iso,))
            row = cur.fetchone()
            
            if not row:
                conn.rollback()
                return None
            
            job_id = row["id"]
            cur.execute("""
                            UPDATE jobs 
                            SET state = 'processing', updated_at = ?
                            WHERE id = ? AND state = 'pending'
                        """, (now_iso, job_id))
            
            if cur.rowcount == 1:
                conn.commit()
                cur.execute("SELECT * from jobs WHERE id=?", (job_id,))
                return dict(cur.fetchone())
            else:
                conn.rollback()
                return None
        except Exception:
            conn.rollback()
            raise 