from datetime import datetime
from functools import reduce
import csv
import sys

date_hours = {}
with open('../meter.csv', newline='') as f:
    reader = csv.reader(f, delimiter=',')
    next(reader) # discard title row
    prevRow = None
    for row in reader:
        date_hour = int(datetime.strptime(datetime.strptime(row[0], "%x %X").strftime("%x %H"), "%x %H").timestamp())
        val = float(row[1])
        if date_hour not in date_hours:
            date_hours[date_hour] = [0, val]
        else:
            date_hours[date_hour][0] = val - date_hours[date_hour][1]
    
hours = [None] * 24
for dh in date_hours:
    hour = datetime.fromtimestamp(dh).hour
    if hours[hour] is None:
        hours[hour] = [date_hours[dh][0]]
    else:
        hours[hour].append(date_hours[dh][0])

print("hour,usage")
for hour in range(24):
    if hours[hour] is None:
        print("{},{}".format(hour, 0))
    else:
        print("{},{:.2f}".format(hour, reduce(lambda acc, x: acc + x, hours[hour]) / len(hours[hour])))
