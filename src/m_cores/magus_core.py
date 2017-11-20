import json

from core_utils.debugger import debug_core_print_d
from libs.rabbit_handler import RabbitHandler

DEBUG = False


class MagusCore:
    def __init__(self, tag, worker_number, input_queue, output_queue):
        self.tag = tag
        self.worker_number = worker_number
        self.args = []
        self.serializer = json

        if input_queue:
            self.in_queue = RabbitHandler(input_queue)
        if output_queue:
            self.out_queue = RabbitHandler(output_queue)

    def _log(self, message):
        if DEBUG:
            debug_core_print_d(self.__class__, self.worker_number, message)

    def run_core(self):
        raise NotImplementedError
