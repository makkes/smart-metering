#!/usr/bin/env bash

set -euo pipefail

export "DAYS=$1"

python3 transform.py > hours.csv
gnuplot hours.gnuplot
