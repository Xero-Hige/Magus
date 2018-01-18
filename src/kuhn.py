import json
import os
import signal
import sys
from sys import stdout

if sys.version_info.major == 3:
    from m_cores.core_anonymize import AnonymizeCore
    from m_cores.core_char_splitter import CharSplitterCore
    from m_cores.core_chars_dumper import CharsEmbeddingCore
    from m_cores.core_fetcher import FetcherCore
    from m_cores.core_hashtags_process import HashtagSplitterCore
    from m_cores.core_joiner import JoinerCore
    from m_cores.core_lower import LowerCore
    from m_cores.core_parser import ParserCore
    from m_cores.core_rchars_dumper import RCharsEmbeddingCore
    from m_cores.core_shortener import ShortenerCore
    from m_cores.core_word_embeding import WordEmbeddingCore
    from m_cores.core_word_splitter import WordSplitterCore
    from m_cores.emitter_core import EmitterCore
    from m_cores.core_strip_accents import StripAccentsCore

    CORES = {
        "fetcher":       FetcherCore,
        "parser":        ParserCore,
        "anonymize":     AnonymizeCore,
        "s_accents":     StripAccentsCore,
        "char_splitter": CharSplitterCore,
        "w_splitter":    WordSplitterCore,
        "shortener":     ShortenerCore,
        "htag_splitter": HashtagSplitterCore,
        "lower":         LowerCore,
        "emitter":       EmitterCore,
        "rchar_embed":   RCharsEmbeddingCore,
        "char_embed":    CharsEmbeddingCore,
        "w_embedding":   WordEmbeddingCore,
        "joiner":        JoinerCore
    }
else:
    from m_cores.core_classifier import ClassifierCore

    CORES = {
        "classifier": ClassifierCore
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
    print("Starting Kuhn")
    cores = []

    if len(sys.argv) > 1:
        struct_file = sys.argv[1]
    else:
        struct_file = "pipeline_struct.json"

    with open(struct_file) as reader_file:
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
        print("[Kuhn] Debug: Handling ", signum)
        stdout.flush()

        for _core in cores:
            _core.stop()

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    for _ in range(len(cores)):
        os.wait()


if __name__ == '__main__':
    main()
