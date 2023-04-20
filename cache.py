import json
import sqlite3

from sqlite3 import Error

from request import Request


def _create_connection(db_file) -> sqlite3.Connection | None:
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def _create_table(conn, create_table_sql) -> None:
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


class Cache:
    _TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    method TEXT NOT NULL,
    url TEXT NOT NULL,
    response TEXT NOT NULL,
    body TEXT NULL,
    headers TEXT NULL,
    data TEXT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (method, url, body, headers, data)
    );"""

    def __init__(self, db_file):
        self.db_file = db_file
        self.initialized = False
        try:
            self.conn = _create_connection(db_file)
            self.initialized = True
            _create_table(self.conn, self._TABLE_SQL)
        except Error as e:
            print("Error while initializing cache: " + str(e))

    def get(self, request: Request) -> str | None:
        if not self.initialized:
            return None

        headers = json.dumps(request.headers) if request.headers else ""
        data = json.dumps(request.data) if request.data else ""

        c = self.conn.cursor()
        c.execute("SELECT response FROM cache WHERE method = ? AND url = ? AND body = ? AND headers = ? AND data = ?",
                  (request.method, request.url, request.body, headers, data))
        result = c.fetchone()

        return result[0] if result else None

    def set(self, request: Request, response: str) -> None:
        if not self.initialized:
            return

        headers = json.dumps(request.headers) if request.headers else ""
        data = json.dumps(request.data) if request.data else ""

        c = self.conn.cursor()
        c.execute("INSERT INTO cache (method, url, response, body, headers, data) VALUES (?, ?, ?, ?, ?, ?)",
                  (request.method, request.url, response, request.body, headers, data))
        self.conn.commit()
