from datetime import datetime
import csv

with open('../meter.csv', newline='') as f:
    daily = {}
    reader = csv.reader(f, delimiter=',')
    next(reader) # discard title row
    for row in reader:
        day = datetime.strptime(row[0], "%x %X").strftime("%x")
        val = float(row[1])
        if day not in daily:
            daily[day] = [val, 0]
        else:
            daily[day][1] = val - daily[day][0]

    print("day,usage")
    for day in daily:
        print("{},{:.2f}".format(day, daily[day][1]))
