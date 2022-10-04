#!/usr/bin/env bash

export "DAYS=$1"

python3 temp.py > temps.csv
gnuplot temps.gnuplot
