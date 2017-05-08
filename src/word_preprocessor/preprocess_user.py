import re

URL_REGEXP = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

def preprocess(word):
    """ """
    updated = False
    if re.match(URL_REGEXP,word):
        word = " URL "
        updated = True

    return word, updated