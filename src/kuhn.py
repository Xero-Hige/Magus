import json
import os
import signal
from sys import stdout

from m_cores import cleaner_core, fetcher_core, parser_core, producer_core

CORES = {
    "cleaner": cleaner_core.main,
    "fetcher": fetcher_core.main,
    "parser": parser_core.main,
    "producer": producer_core.main
}


class DetachedCore():
    def __init__(self, main_function, tag, worker_number, in_queue, out_queue):
        pid = os.fork()
        if pid == 0:
            result = main_function(tag, worker_number, in_queue, out_queue)
            exit(result)
        else:
            self.pid = pid

    def stop(self):
        if self.pid != 0:
            os.kill(self.pid, signal.SIGTERM)

    def dispatch_signal(self, signum):
        if self.pid != 0:
            os.kill(self.pid, signum)


def main():
    cores = []

    structure = {}

    with open("pipeline_struct.json") as reader_file:
        structure = json.loads(reader_file.read())

    for definition_name in structure:
        core_def = structure[definition_name]

        core_tag = core_def["tag"]
        core_replicas = core_def["replicas"]
        core_inqueue = core_def["input_queue"]
        core_outqueue = core_def["output_queue"]

        for worker_number in range(1, core_replicas + 1):
            core = DetachedCore(CORES[core_tag], core_tag, worker_number, core_inqueue, core_outqueue)
            cores.append(core)

    def handler(signum, frame):
        print ("[Kuhn] Debug: Handling ", signum)
        stdout.flush()

        for _core in cores:
            _core.stop()

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    for _ in range(len(cores)):
        os.wait()


if __name__ == '__main__':
    main()
