from libs.rabbit_handler import RabbitHandler
from m_cores.magus_core import MagusCore

DEBUG = False


class MagusDumpCore(MagusCore):
    def run_core(self):
        raise NotImplementedError

    def __init__(self, input_queue, output_queue, tag, worker_number):
        MagusCore.__init__(self, tag, worker_number, input_queue, output_queue)
        self.dump_queue = RabbitHandler("MERGER")
