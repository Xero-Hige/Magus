import json
import os
import signal
from sys import stdout

from m_cores.core_anonymize import AnonymizeCore
from m_cores.core_fetcher import FetcherCore
from m_cores.core_hashtags_process import HashtagSplitterCore
from m_cores.core_parser import ParserCore
from m_cores.core_word_lower import WordLowerCore
from m_cores.core_word_shortener import WordShortenerCore
from m_cores.core_word_splitter import WordSplitterCore
from m_cores.emitter_core import EmitterCore

CORES = {
    "fetcher": FetcherCore,
    "parser": ParserCore,
    "anonymize": AnonymizeCore,
    "w_splitter": WordSplitterCore,
    "w_shortener": WordShortenerCore,
    "htag_splitter": HashtagSplitterCore,
    "w_lower": WordLowerCore,
    "emitter": EmitterCore
}


class DetachedCore:
    def __init__(self, core_class, tag, worker_number, in_queue, out_queue):
        pid = os.fork()
        if pid == 0:
            core = core_class(in_queue, out_queue, tag, worker_number)
            result = core.run_core()
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
