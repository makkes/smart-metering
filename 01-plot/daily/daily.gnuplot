set term png size 1920,1080
set output "../../02-out/daily.png"
set key autotitle columnhead
set datafile separator ","
set xdata time
set timefmt "%m/%d/%y"
set format x "%m/%d/%y"
set ylabel "m³"
set y2label "°C"
set y2tics 1
set grid y2tics
set xlabel "day"
set style fill solid
set boxwidth 0.5 relative
set xtics rotate 86400
plot "< tail -n${DAYS} daily.csv" using 1:2 with lines title "gas use",\
     "< tail -n${DAYS} ../temp/temps.csv" using 1:2 with lines lt rgb "#98A8FA" title "temperature" axis x1y2
