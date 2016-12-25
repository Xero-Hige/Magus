#!/usr/bin/env bash
rabbitmq-server &
sleep 4
rabbitmqctl start_app
export PYTHONIOENCODING=utf-8
python3 tweets_fetcher.py &
python3 tweets_splitter.py &
python3 tweets_splitter.py &
python3 tweets_process.py &
python3 tweets_process.py &
python3 tweet_tokenizer.py
