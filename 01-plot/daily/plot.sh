#!/usr/bin/env bash

set -euo pipefail

python3 transform.py > daily.csv
gnuplot daily.gnuplot
