import psycopg2


class Migration:
    def __init__(self, id, ddls):
        self.id = id
        self.ddls = ddls


class DB:
    def __init__(self, host, port, dbname, user, password):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password

    def connect(self, autocommit=True):
        conn = psycopg2.connect(
            f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} password={self.password}")
        conn.set_session(autocommit=autocommit)
        return conn

    def init_version_table(self):
        with self.connect(autocommit=False) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'versions'")
                res = cur.fetchone()
                if res[0] != 1:
                    cur.execute(
                        "CREATE table versions(id VARCHAR(32) NOT NULL, seq SMALLINT NOT NULL, created_at TIMESTAMP NOT NULL DEFAULT NOW(), PRIMARY KEY(id, seq))")

    def migrate(self, migrations):
        with self.connect(autocommit=False) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT seq FROM versions WHERE id = %s ORDER BY seq DESC LIMIT 1", (migrations.id,))
                res = cur.fetchone()
                if res == None:
                    latest_seq = -1
                else:
                    latest_seq = res[0]
                for idx, ddl in enumerate(migrations.ddls):
                    if idx > latest_seq:
                        print(f'running migration {idx} for {migrations.id}')
                        cur.execute(ddl)
                        cur.execute("INSERT INTO versions(id, seq) VALUES(%s, %s)", (migrations.id, idx))
