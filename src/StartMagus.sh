#!/usr/bin/env bash
rabbitmq-server &
sleep 4
rabbitmqctl start_app
export PYTHONIOENCODING=utf-8
python3 tweetsFetcher.py &
python3 splitter.py