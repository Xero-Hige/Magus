import re

URL_TAG = "http://URL"
USER_TAG = "@USER"


def censor_urls(text):
    for url in re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text):
        text = text.replace(url, URL_TAG)
    return text


def anonymize_usernames(text):
    for word in text.split():
        if len(word) > 1 and word[0] == '@' and word[1:].isalpha():
            text = text.replace(word, USER_TAG)
    return text


def full_anonymize_tweet(tweet_text):
    return censor_urls(anonymize_usernames(tweet_text))
