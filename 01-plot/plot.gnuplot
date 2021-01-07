set term png
set output "../02-out/chart.png"
set key autotitle columnhead
set datafile separator ","
set xdata time
set timefmt "%m/%d/%y %H:%M:%S"
set format x "%m/%d/%y %H:%M:%S"
set ylabel "m³"
set xlabel "time"
set grid
set xtics rotate
plot "meter.csv" using 1:2 with steps
