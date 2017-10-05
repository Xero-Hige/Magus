class TrainSentenceGenerator():

    def __init__(self,dirs,tokenizer):
        self.dirs = dirs
        self.tokenizer = tokenizer

    def __iter__(self):
        for directory in self.dirs:
            for file in os.walk(directory):
                path = os.path.join(directory,file)
                #load
