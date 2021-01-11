set term png
set output "../../02-out/hours.png"
set key autotitle columnhead
set datafile separator ","
set ylabel "m³"
set xlabel "hour"
set xrange [-1:24]
set style fill solid
set boxwidth 0.5 relative
set xtics 1
plot "hours.csv" using 1:2 with boxes
