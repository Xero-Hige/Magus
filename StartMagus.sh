#!/usr/bin/env bash
docker build -t xerohige/magus .
docker run --name "Magus" xerohige/magus