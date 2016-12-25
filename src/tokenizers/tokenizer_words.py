def tokenize(tweet):
    tokens = {}

    text = tweet["processed_text"]

    for word in text.split():
        tokens[word] = tokens.get(word, 0) + 1

    return tokens
