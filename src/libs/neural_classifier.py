import random

from libs.sentiments_handling import ANGRY, HAPPY, NONE, SAD

INPUT_SIZE = 3
INPUT_LEN = 3
OUTPUT_LEN = 9


class NeuralClassifier():
    def __init__(self):
        pass

    def classify(self, input_matrix):
        # Baseline
        # return [random.random() for _ in range(OUTPUT_LEN)]
        return random.choice([HAPPY, ANGRY, SAD, HAPPY, ANGRY, SAD, HAPPY, ANGRY, SAD, NONE])
