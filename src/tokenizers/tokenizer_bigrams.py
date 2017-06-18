def tokenize(tweet):
    tokens = {}
    text = tweet["text"]

    for i in range(len(text) - 2):
        tokens[text[i:i + 2]] = tokens.get(text[i:i + 2], 0) + 1

    return tokens
