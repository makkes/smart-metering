set term png size 1600,900
set output "../../02-out/temps.png"
set key autotitle columnhead
set datafile separator ","
set xdata time
set timefmt "%m/%d/%y"
set format x "%m/%d/%y"
set ylabel "°C"
set xlabel "day"
#set xtics rotate 604800
set xtics rotate 86400
set ytics 1
set grid ytics
set style fill transparent solid 0.4 noborder
plot "< tail -n${DAYS} temps.csv" using 1:3:4 with filledcurves lt rgb "#9BFA98" title "min/max",\
     "< tail -n${DAYS} temps.csv" using 1:2 with lines lt rgb "#98A8FA" title "avg"
