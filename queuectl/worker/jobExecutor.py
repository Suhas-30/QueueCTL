import subprocess
from datetime import datetime, timezone
from queuectl.dbConnection import getConnection
from queuectl.worker.retry import retryTask
def updateJobState(jobId, state, lastError=None):
    now_iso = datetime.now(timezone.utc).isoformat()
    with getConnection() as conn:
        cur = conn.cursor()
        cur.execute("""
                    UPDATE jobs
                    SET state = ?, last_error=?, updated_at = ?
                    WHERE id=?
                    """, (state, lastError, now_iso, jobId))
        conn.commit()

def runJob(job):
    jobId = job["id"]
    command = job["command"]
    print(f"[Executor] running job {jobId}: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode==0:
            print(f"[Executor] job {jobId} completed successfully.")
            updateJobState(jobId, "completed")
        else:
            print(f"[Executor] Job {jobId} failed. Scheduling retry...")
            retryTask(job)
    except Exception as e:
        print(f"[Executor] Exception running job {jobId}: {e}")
        retryTask(job)