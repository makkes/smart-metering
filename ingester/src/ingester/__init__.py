import csv
from datetime import datetime, timezone
import logging
import psycopg2
from psycopg2.extras import execute_values
import pytz


def prepare_tables(conn):
    tables = {
        "gas": "CREATE TABLE gas(dt TIMESTAMP WITH TIME ZONE NOT NULL, reading NUMERIC(7,2) NOT NULL, PRIMARY KEY(dt))",
        "gas_per_day": "CREATE TABLE gas_per_day(day DATE NOT NULL, consumption NUMERIC(7,2) NOT NULL, PRIMARY KEY(day))"
    }
    with conn.cursor() as cur:
        for name, ddl in tables.items():
            cur.execute(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = %s", (name,))
            res = cur.fetchone()
            if res[0] != 1:
                cur.execute(ddl)


def ingest(f, conn):
    with conn.cursor() as cur:
        start_ts = None
        # fetch most recent day from DB
        cur.execute("SELECT dt FROM gas ORDER BY dt DESC LIMIT 1")
        res = cur.fetchone()
        if res != None:
            start_ts = res[0]

        with open(f, newline='') as c:
            rdr = csv.reader(c, delimiter=',')
            next(rdr)  # discard title row
            inserts = []
            for row in rdr:
                dt = pytz.timezone("CET").localize(datetime.strptime(row[0], "%m/%d/%y %H:%M:%S"))
                if start_ts is not None and dt <= start_ts:
                    continue
                inserts.append((dt.strftime("%Y-%m-%d %H:%M:%S%z"), row[1]))
        try:
            logging.info("inserting %s %s", len(inserts), "row" if len(inserts) == 1 else "rows")
            execute_values(
                cur, "INSERT INTO gas(dt, reading) VALUES %s ON CONFLICT(dt) DO NOTHING", inserts)
        except Exception as e:
            logging.info("error inserting data: %s", e)


def update_per_day_consumption(conn):
    cur = conn.cursor()
    start_day = None
    # fetch most recent day from DB
    cur.execute("SELECT day FROM gas_per_day ORDER BY DAY DESC LIMIT 1")
    res = cur.fetchone()
    if res != None:
        start_day = res[0]

    per_day_consumption = {}
    cur.execute("SELECT dt, reading FROM gas")
    res = cur.fetchall()
    for single_reading in res:
        day = single_reading[0].date()
        if start_day is not None and day < start_day:
            continue
        try:
            pdc = per_day_consumption[day]
            reading = single_reading[1]
            if reading < pdc[0]:
                pdc[0] = reading
            if reading > pdc[1]:
                pdc[1] = reading
            pdc[2] = pdc[1] - pdc[0]
        except KeyError:
            pdc = [single_reading[1], single_reading[1], 0]
        per_day_consumption[day] = pdc
    for day, vals in per_day_consumption.items():
        cur.execute(
            "INSERT INTO gas_per_day(day, consumption) VALUES(%s, %s) ON CONFLICT (day) DO UPDATE SET consumption = %s", (day, vals[2], vals[2]))
        logging.info("inserted/updated daily consumption for %s", day)
