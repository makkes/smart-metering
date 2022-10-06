import csv
import psycopg2
from collections import defaultdict

def init_db_conn(host, port, dbname, user, password):
    conn = psycopg2.connect(f"host={host} port={port} dbname={dbname} user={user} password={password}")
    conn.set_session(autocommit=True)
    return conn

def prepare_tables(conn):
    tables = {
            "gas": "CREATE TABLE gas(dt TIMESTAMP WITH TIME ZONE NOT NULL, reading NUMERIC(7,2) NOT NULL, PRIMARY KEY(dt))",
            "gas_per_day": "CREATE TABLE gas_per_day(day DATE NOT NULL, consumption NUMERIC(7,2) NOT NULL, PRIMARY KEY(day))"
            }
    with conn.cursor() as cur:
        for name, ddl in tables.items():
            cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = %s", (name,))
            res = cur.fetchone()
            if res[0] != 1:
                cur.execute(ddl)

def ingest(f, conn):
    cur = conn.cursor()
    with open(f,newline='') as c:
        rdr = csv.reader(c, delimiter=',')
        next(rdr) # discard title row
        for row in rdr:
            try:
                row[0] += " CEST"
                cur.execute("INSERT INTO gas(dt, reading) VALUES(%s, %s)", (row[0], row[1]))
                print("inserted reading ({}, {})".format(row[0], row[1]))
            except psycopg2.errors.UniqueViolation:
                pass
    cur.execute("SELECT * FROM gas;")
    cur.close()

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
        if day < start_day:
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
        cur.execute("INSERT INTO gas_per_day(day, consumption) VALUES(%s, %s) ON CONFLICT (day) DO UPDATE SET consumption = %s", (day, vals[2], vals[2]))
        print("inserted/updated daily consumption for {}".format(day))
