#!/usr/bin/env bash
export PYTHONIOENCODING=utf-8
sleep 10
gunicorn the_world:app -b 0.0.0.0:8000