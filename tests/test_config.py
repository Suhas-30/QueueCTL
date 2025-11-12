import pytest 
from queuectl.config import ConfigRepo

def testSetandGetConfig():
    repo = ConfigRepo()
    repo.setConfig("max-retries", 3)
    value = repo.getConfig("max-retries")
    value = repo.getConfig("max-retries")
    assert value == "3"