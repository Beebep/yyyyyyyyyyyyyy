#!/usr/bin/env bash


python3 ./src/mlp.py
gsutil cp out gs://data-filip/
