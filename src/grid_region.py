import time
from threading import Lock


class GridRegion:
    ANTICIPATION = 0
    ANGER = 1
    DISGUST = 2
    SADNESS = 3
    SURPRISE = 4
    FEAR = 5
    TRUST = 6
    JOY = 7
    NEUTRAL = 8

    __ACUMULATED = 9

    TIME_SLICE = 60
    DEFAULT_TIME_SLICES = 60

    def __init__(self, slices_history=DEFAULT_TIME_SLICES, slice_size=TIME_SLICE):
        self.slice_size = slice_size
        self.lock = Lock()

        self.statics = [0 for _ in range(self.__ACUMULATED + 1)]
        self.queue = [[0 for _ in range(self.__ACUMULATED + 1)] for _ in range(slices_history)]
        self.actual = [0 for _ in range(self.__ACUMULATED + 1)]
        self.timestamp = time.time()

    def add(self, classification):
        with self.lock:
            self.actual[classification] += 1
            self.actual[self.__ACUMULATED] += 1

            if time.time() - self.timestamp > self.slice_size:
                self.__update_region()

    def __update_region(self):
        self.queue.append(self.actual)
        for i in range(len(self.actual)):
            self.statics[i] += self.actual[i]
        removed = self.queue.pop(0)
        for i in range(len(self.actual)):
            self.statics[i] -= removed[i]

        self.actual = [0 for _ in range(self.__ACUMULATED + 1)]

    def get(self):
        with self.lock:
            if self.statics[-1] == 0:
                return self.NEUTRAL, 1

            max_index = 0
            for i in range(len(self.statics) - 1):
                if self.statics[i] >= self.statics[max_index]:
                    max_index = i
            return max_index, self.statics[max_index] / self.statics[-1]
