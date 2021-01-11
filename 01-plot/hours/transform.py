from datetime import datetime
from functools import reduce
import csv

date_hours = {}
with open('../meter.csv', newline='') as f:
    reader = csv.reader(f, delimiter=',')
    next(reader) # discard title row
    prevRow = None
    for row in reader:
        date_hour = int(datetime.strptime(datetime.strptime(row[0], "%x %X").strftime("%x %H"), "%x %H").timestamp())
        val = float(row[1])
        if date_hour not in date_hours:
            date_hours[date_hour] = [val]
        else:
            date_hours[date_hour].append(val)
    
hours = [None] * 24
for dh in date_hours:
    delta = date_hours[dh][len(date_hours[dh]) - 1] - date_hours[dh][0]
    if delta == 0:
        continue
    hour = datetime.fromtimestamp(dh).hour
    if hours[hour] is None:
        hours[hour] = [delta]
    else:
        hours[hour].append(delta)

print("hour,average usage")
for hour in range(24):
    print("{},{}".format(hour, reduce(lambda acc, x: acc + x, hours[hour]) / len(hours[hour])))
