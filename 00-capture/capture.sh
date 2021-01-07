#!/usr/bin/env bash

set -euo pipefail

python3 capture.py $1 | tee -a ../01-plot/meter.csv
