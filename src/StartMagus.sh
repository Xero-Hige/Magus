#!/usr/bin/env bash
rabbitmq-server &
sleep 4
rabbitmqctl start_app
export PYTHONIOENCODING=utf-8
python3 tweets_fetcher.py Fetcher&
python3 tweets_splitter.py Splitter1&
python3 tweets_splitter.py Splitter2&
python3 tweets_pre-process_raw.py RawProcess1&
python3 tweets_pre-process_raw.py RawProcess2&
python3 tweets_pre-process_lowercase.py FullProcess1&
python3 tweets_pre-process_lowercase.py FullProcess2&
python3 tweet_tokenizer.py Tokenizer
