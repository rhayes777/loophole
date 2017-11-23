#!/usr/bin/env bash

python main.py $1 $2 | python visual.py -i
