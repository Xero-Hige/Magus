#!/usr/bin/env bash
rabbitmq-server &
sleep 4
rabbitmqctl start_app
export PYTHONIOENCODING=utf-8
sleep 5
python3 khun.py
sleep 4
#python3 tweets_splitter.py splitter1&
#python3 tweets_splitter.py splitter2&
#python3 tweets_pre-process_raw.py &
#python3 tweets_pre-process_raw.py &
#python3 tweets_pre-process_lowercase.py lower1&
#python3 tweets_pre-process_lowercase.py lower2&
#python3 tweet_tokenizer.py Tokenizer1 &
#python3 tweet_tokenizer.py Tokenizer2 &
#python3 trainer_totalizer.py Totalizer

