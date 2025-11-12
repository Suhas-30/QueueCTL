import time
import os
from queuectl.worker.jobExecutor import runJob
from queuectl.worker.jobLifeCycle import pickJob
from queuectl.worker.shutdown import setupSignalHandlers, shutdownFlag

def workerLoop():
    print(f"[Worker PID {os.getpid()}] loop started")
    setupSignalHandlers()

    while not shutdownFlag.is_set():
        job = pickJob()
        if job:
            runJob(job)
        else:
            time.sleep(1)
            
    print(f"[Worker PID {os.getpid()}] exiting gracefully after current job.")
