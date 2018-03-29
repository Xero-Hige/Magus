#!/usr/bin/env bash
set -e
python3 embeddings_generator.py
python3 morgana_train_data_builder.py
python3 morgana_trainer.py 25 "Morgana" 2 0
rm -rf Morgana/1
mv Morgana/2 Morgana/1
