import os

def get_preprocessors(excluded=[]):
    lst = os.listdir("word_preprocessor")

    modules = []

    for x in lst:
        x = x.replace(".py", "")
        x = "word_preprocessor." + x
        modules.append(__import__(x, fromlist=['']))

    return [module for module in modules if "__" not in module.__name__ and module.__name__ not in excluded]


print (get_preprocessors())
