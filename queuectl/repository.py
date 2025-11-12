from .dbConnection import getConnection, initializeDB
import uuid 
from datetime import datetime

class JobRepository:
    def __init__(self):
        initializeDB()
        
    def addJob(self, command, max_retries):
        job_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        with getConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                            INSERT INTO jobs (id, command, state, attempts, max_retries, created_at, updated_at) 
                            VALUES (?, ?, 'pending', 0, ?, ?, ?)
                           """, (job_id, command, max_retries, now, now))
            conn.commit()
            return job_id
