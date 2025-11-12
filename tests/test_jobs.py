import pytest 
from queuectl.repository import JobRepository

def testEnqueueAndListjobs():
    repo = JobRepository()
    job_Id = repo.addJob("echo 'Test Job'", 3)
    assert job_Id is not None
    
