import csv
import os
import tempfile
import time
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile

import psycopg2


def prepare_tables(conn):
    tables = {
        "temperatures": "CREATE TABLE temperatures(day DATE NOT NULL, min NUMERIC(3,1) NOT NULL, max NUMERIC(3,1) NOT NULL, avg NUMERIC(3,1) NOT NULL, PRIMARY KEY(day))",
    }
    with conn.cursor() as cur:
        for name, ddl in tables.items():
            cur.execute(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = %s", (name,))
            res = cur.fetchone()
            if res[0] != 1:
                cur.execute(ddl)


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
        with db_conn.cursor() as cur:
            for row in r:
                date = row[idxs["date"]].strip()
                avg_t = float(row[idxs["avg"]].strip())
                min_t = float(row[idxs["min"]].strip())
                max_t = float(row[idxs["max"]].strip())
                try:
                    cur.execute(
                        "INSERT INTO temperatures(day, min, max, avg) VALUES(%s, %s, %s, %s)", (date, min_t, max_t, avg_t))
                    print(f"inserted ({date}, {min_t}, {avg_t}, {max_t})")
                except psycopg2.errors.UniqueViolation:
                    pass
