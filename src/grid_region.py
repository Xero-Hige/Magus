import time
from threading import Lock

CLASSES = 4


class GridRegion:
    HAPPY = 0
    SAD = 1
    ANGRY = 2
    INDIFERENT = 3

    TIME_SLICE = 60
    DEFAULT_TIME_SLICES = 60

    def __init__(self, slices_history=DEFAULT_TIME_SLICES, slice_size=TIME_SLICE):
        self.slice_size = slice_size
        self.lock = Lock()

        self.statics = [0, 0, 0, 0]
        self.queue = [[0, 0, 0, 0] for _ in range(slices_history)]
        self.actual = [0, 0, 0, 0]
        self.timestamp = time.time()

    def add(self, classification):
        with self.lock:
            self.actual[classification] += 1

            if time.time() - self.timestamp > self.slice_size:
                self.__update_region()

    def __update_region(self):
        self.queue.append(self.actual)
        for i in range(CLASSES):
            self.statics[i] += self.actual[i]
        removed = self.queue.pop(0)
        for i in range(CLASSES):
            self.statics[i] -= removed[i]

    def get(self):
        with self.lock:
            return self.actual[:]
