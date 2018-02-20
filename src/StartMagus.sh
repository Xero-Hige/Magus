#!/usr/bin/env bash
export PYTHONIOENCODING=utf-8
hostip=$(ip route show)
echo $hostip
sleep 10
python  kuhn.py pipeline_struct_tensors.json &
python3 kuhn.py pipeline_struct.json