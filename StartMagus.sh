#!/usr/bin/env bash
docker build -t xerohige/magus .
docker run -v train_results:/trainresults --name "Magus" xerohige/magus