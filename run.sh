#!/usr/bin/env bash

# python main.py $1 $2 | python visual.py -i
python src $1 $2 | python -m src.visual -i
