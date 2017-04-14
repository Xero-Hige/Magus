import os


def get_preprocessors(excluded=[]):
    lst = os.listdir("tokenizers")

    modules = []

    for x in lst:
        x = x.replace(".py", "")
        x = "preprocess." + x
        modules.append(__import__(x, fromlist=['']))

    return [module for module in modules if "__" not in module.__name__ and module.__name__ not in excluded]
