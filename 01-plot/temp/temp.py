from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import os
import time
import csv

def refresh_data(out):
    with urlopen("https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/recent/tageswerte_KL_01981_akt.zip") as resp:
        with ZipFile(BytesIO(resp.read())) as archive:
            for name in archive.namelist():
                if name.startswith("produkt_klima_tag_"):
                    archive.extract(name)
                    os.rename(name, out)

def print_temps(fname):
    print("date,avg,min,max")
    with open(fname, newline='') as csvfile:
        r = csv.reader(csvfile, delimiter=';')
        header = next(r)
        idxs = {}
        for idx, hname in enumerate(header):
            hname = hname.strip()
            if hname == "MESS_DATUM":
                idxs["date"] = idx
            elif hname == "TMK":
                idxs["avg"] = idx
            elif hname == "TXK":
                idxs["max"] = idx
            elif hname == "TNK":
                idxs["min"] = idx
        for row in r:
            date = time.strptime(row[idxs["date"]].strip(), "%Y%m%d")
            avg_t = float(row[idxs["avg"]].strip())
            min_t = float(row[idxs["min"]].strip())
            max_t = float(row[idxs["max"]].strip())
            print("{},{},{},{}".format(time.strftime("%x", date), avg_t, min_t, max_t))

if __name__ == "__main__":
    data_fname = "data.csv"
    try:
        s = os.stat(data_fname)
        if time.time() - s.st_ctime > 86400:
            refresh_data(data_fname)
    except FileNotFoundError:
            refresh_data(data_fname)
    print_temps(data_fname)
