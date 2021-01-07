set term png
set output "../../02-out/daily.png"
set key autotitle columnhead
set datafile separator ","
set xdata time
set timefmt "%m/%d/%y"
set format x "%m/%d/%y"
set ylabel "m³"
set xlabel "day"
set style fill solid
set boxwidth 0.5 relative
set xtics rotate 86400
plot "daily.csv" using 1:2 with boxes,\
     "daily.csv" using 1:2:2 with labels
