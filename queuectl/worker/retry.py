from datetime import datetime, timezone, timedelta
from queuectl.dbConnection import getConnection
from queuectl.config import ConfigRepo
configRepo = ConfigRepo()

def retryTask(job, base: int = 2):
    base  = int(configRepo.getConfig("backoff-base", 2))
    maxRetries = int(configRepo.getConfig("max-retries", job["max_retries"]))
    jobId = job["id"]
    attempts = job["attempts"] + 1
    maxRetries = job["max_retries"]
    
    now = datetime.now(timezone.utc)
    delay = base ** attempts
    nextRetry = now + timedelta(seconds=delay)
    
    with getConnection() as conn:
        cur = conn.cursor()
        if attempts >= maxRetries:
            cur.execute("""
                UPDATE jobs 
                SET state = 'dead',
                    attempts = ?,
                    updated_at = ?,
                    last_error = ?
                WHERE id = ?
            """, (attempts, now.isoformat(), "Max retries exceeded", jobId))
            print(f"[Retry] Job {jobId} moved to DLQ after {attempts} attempts.")
        else:
            cur.execute("""
                UPDATE jobs 
                SET state = 'pending',
                    attempts = ?,
                    next_retry_at = ?,
                    updated_at = ?,
                    last_error = ?
                WHERE id = ?
            """, (attempts, nextRetry.isoformat(), now.isoformat(), "Scheduled for retry", jobId))
            print(f"[Retry] Job {jobId} scheduled to retry at {nextRetry.isoformat()}")
        conn.commit()
