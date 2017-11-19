#!/usr/bin/env bash
export PYTHONIOENCODING=utf-8
sleep 10
python  kuhn.py pipeline_struct_tensors.json &
python3 kuhn.py