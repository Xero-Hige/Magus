def tokenize(tweet):
    tokens = {}
    return tokens  # FIXME
    text = tweet["processed_text"]

    for i in range(len(text) - 2):
        tokens[text[i:i + 2]] = tokens.get(text[i:i + 2], 0) + 1

    return tokens
