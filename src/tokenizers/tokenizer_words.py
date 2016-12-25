def tokenize(text, tweet):
    tokens = {}

    for word in text.split():
        tokens[word] = tokens.get(word, 0) + 1

    return tokens
