def tokenize(tweet):
    return {}
    tokens = {}

    text = tweet["cleaned_text"].lower()

    for word in text.split():
        tokens[word] = tokens.get(word, 0) + 1

    return tokens
