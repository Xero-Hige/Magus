#!/usr/bin/env bash
rabbitmq-server &
sleep 4
rabbitmqctl start_app
export PYTHONIOENCODING=utf-8
sleep 5
python3 trainer_fetcher.py &
sleep 4
python3 tweets_splitter.py &
python3 tweets_splitter.py &
python3 tweets_pre-process_raw.py &
python3 tweets_pre-process_raw.py &
python3 tweets_pre-process_lowercase.py FullProcess1&
python3 tweets_pre-process_lowercase.py FullProcess2&
python3 tweet_tokenizer.py Tokenizer
