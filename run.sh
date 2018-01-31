#!/usr/bin/env bash

# python main.py $1 $2 | python visual.py -i
python python $1 $2 | python -m python.visual -i
