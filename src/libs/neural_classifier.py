INPUT_SIZE = 3
INPUT_LEN = 3
OUTPUT_LEN = 9

class NeuralClassifier():

    def __init__(self):
        pass

    def classify(self,input_matrix):
        return [ random.random() for _ in range(OUTPUT_LEN) ]
