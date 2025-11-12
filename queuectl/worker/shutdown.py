import signal
import multiprocessing

shutdownFlag = multiprocessing.Event()

def handleShutdown(signum, frame):
    print(f"\n[worker] Recived signal {signum}, shutting down gracefully..")
    shutdownFlag.set()
    
def setupSignalHandlers():
    signal.signal(signal.SIGINT, handleShutdown)
    try:
        signal.signal(signal.SIGTERM, handleShutdown)
    except AttributeError:
        pass