#!/usr/bin/env bash
docker build -t xerohige/magus .
docker run -v $(pwd)/train_results:/trainresults --name "Magus" xerohige/magus
