def preprocess(word):
    """ """
    updated = False
    if len(word) > 1 and word[0] == '#' and word[1].isalpha():
        word = " HTAG" + word[1:]
        updated = True

    return (word, updated)
