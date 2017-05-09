def preprocess(word):
    """ """
    updated = False
    if word[0] == "@":
        word = "@USER"
        updated = True

    return word, updated