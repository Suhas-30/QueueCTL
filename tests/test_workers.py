from queuectl.worker.jobExecutor import runJob

def testRunValidJob():
    job = {
        "id":"123",
        "command": "echo 'pytest job'",
        "attempts" : 0,
        "max_retries":3
    }
    runJob(job)
    