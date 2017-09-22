import os
import signal

from m_cores import fetcher_core

CORES = {
    "fectcher": fetcher_core.main
}


class DetachedCore():
    def __init__(self, main_function):
        pid = os.fork()
        if pid == 0:
            result = main_function()
            exit(result)
        else:
            self.pid = pid

    def stop(self):
        if self.pid != 0:
            os.kill(self.pid, signal.SIGTERM)

    def dispatch_signal(self, signal):
        if self.pid != 0:
            os.kill(self.pid, signal.SIGTERM)


def main():
    cores = []

    for _ in range(1):
        core = DetachedCore(CORES["fectcher"])
        cores.append(core)

    def handler(signum, frame):
        print ("handling: ", signum)
        for _core in cores:
            _core.stop()

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    for _ in range(len(cores)):
        os.wait()

    print ("Ended")


if __name__ == '__main__':
    main()
