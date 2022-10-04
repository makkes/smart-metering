#!/usr/bin/env bash

set -euo pipefail

export "DAYS=$1"

python3 transform.py > daily.csv
gnuplot daily.gnuplot
