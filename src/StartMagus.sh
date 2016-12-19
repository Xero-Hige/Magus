#!/usr/bin/env bash
rabbitmq-server &
sleep 4
rabbitmqctl start_app
python3 tweetsFetcher.py