#!/usr/bin/env bash

set -euo pipefail

export "DAYS=$1"

gnuplot plot.gnuplot
sed -i "s/\(<h1 class=\"current\">\).*\(<\/h1>\)/\\1$(tail -n1 meter.csv | sed 's/,/: /' | sed 's/\//\\\//g')\\2/" ../02-out/index.html
