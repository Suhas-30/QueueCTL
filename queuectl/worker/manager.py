import os
import signal
from multiprocessing import Process
from queuectl.worker.workLoop import workerLoop
from queuectl.worker.shutdown import setupSignalHandlers, shutdownFlag

def _runWorker():
    setupSignalHandlers()
    workerLoop()
    
def startWorkers(count: int = 1):
    procs = []
    print(f"[Manger PID {os.getpid()} Starting {count} workers...]")
    for i in range(count):
        p = Process(target=_runWorker, name=f"worker-{i+1}")
        p.start()
        procs.append(p)
        print(f"[Manager] started pid={p.pid} name={p.name}")
    try:
        for p in procs:
            p.join()
    except KeyboardInterrupt:
        print("[Manager] KeyboardInterrupt received, forwarding shutdown...")
        shutdownFlag.set()
        for p in procs:
            p.join()
    finally:
        print("[Manager] all workers stopped.")
