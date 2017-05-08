import re

def preprocess(word):
    """ """
    updated = False
    if len(word) > 1 and word[0] == '#' and word[1].isalpha():
        word = " HTAG" + word[1:].lower()
        updated = True

    return word, updated


for url in re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text):
    text = text.replace(url, " URL ")