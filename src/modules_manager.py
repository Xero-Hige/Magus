import os

WORD_PREPROCESSORS_PATH = "word_preprocessor"
TOKENIZERS_PATH = "tokenizers"


class ModulesManager:
    def __init__(self):
        raise Exception("Must not be instantiated")

    @staticmethod
    def get_preprocessors(excluded=()):
        lst = os.listdir("%s" % WORD_PREPROCESSORS_PATH)

        modules = []

        for x in lst:
            x = x.replace(".py", "")
            x = WORD_PREPROCESSORS_PATH + "." + x
            modules.append(__import__(x, fromlist=['']))

        return [module for module in modules if "__" not in module.__name__ and module.__name__ not in excluded]

    @staticmethod
    def get_tokenizers(excluded=()):
        lst = os.listdir("%s" % TOKENIZERS_PATH)

        modules = []

        for x in lst:
            x = x.replace(".py", "")
            x = TOKENIZERS_PATH + "." + x
            modules.append(__import__(x, fromlist=['']))

        return [module for module in modules if "__" not in module.__name__ and module.__name__ not in excluded]


print (ModulesManager.get_preprocessors())
