#!/usr/bin/env bash

set -euo pipefail

python3 transform.py > hours.csv
gnuplot hours.gnuplot
