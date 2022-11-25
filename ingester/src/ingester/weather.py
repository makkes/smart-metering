import csv
import os
import tempfile
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import psycopg2

from . import database


def prepare_tables(db):
    migration = database.Migration("weather", [
        "CREATE TABLE temperatures(day DATE NOT NULL, min NUMERIC(3,1) NOT NULL, max NUMERIC(3,1) NOT NULL, avg NUMERIC(3,1) NOT NULL, PRIMARY KEY(day))",
        "ALTER TABLE temperatures ADD COLUMN precipitation NUMERIC(3,1)",
        "ALTER TABLE temperatures ALTER COLUMN min DROP NOT NULL, ALTER COLUMN max DROP NOT NULL, ALTER COLUMN avg DROP NOT NULL",
    ])
    db.migrate(migration)


def fetch_data():
    with urlopen("https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/recent/tageswerte_KL_01981_akt.zip") as resp:
        with ZipFile(BytesIO(resp.read())) as archive:
            for name in archive.namelist():
                if name.startswith("produkt_klima_tag_"):
                    tmpdirname = tempfile.mkdtemp()
                    archive.extract(name, path=tmpdirname)
                    return os.path.join(tmpdirname, name)
    return None  # this should not happen and should be treated as an error


def insert_temps(data_file, db_conn):
    with open(data_file, newline='') as csvfile:
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
            elif hname == "RSK":
                idxs["precipitation"] = idx
        with db_conn.cursor() as cur:
            for row in r:
                date = row[idxs["date"]].strip()
                avg_t = float(row[idxs["avg"]].strip())
                if avg_t == -999:
                    avg_t = None
                min_t = float(row[idxs["min"]].strip())
                if min_t == -999:
                    min_t = None
                max_t = float(row[idxs["max"]].strip())
                if max_t == -999:
                    max_t = None
                preci = float(row[idxs["precipitation"]].strip())
                print(
                    f"inserting ({date}, {min_t}, {avg_t}, {max_t}, {preci})")
                cur.execute(
                    "INSERT INTO temperatures(day, min, max, avg, precipitation) VALUES(%(day)s, %(min)s, %(max)s, %(avg)s, %(precipitation)s) ON CONFLICT (day) DO UPDATE SET min = %(min)s, max = %(max)s, avg = %(avg)s, precipitation = %(precipitation)s", {"day": date, "min": min_t, "max": max_t, "avg": avg_t, "precipitation": preci})
