import json
import sqlite3
from datetime import datetime
from sqlite3 import Error

from server.request import Request


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


def _get_current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_file)

    def __init__(self, db_file):
        self.db_file = db_file
        self.initialized = False
        try:
            with self.connect() as conn:
                _create_table(conn, self._TABLE_SQL)
            self.initialized = True
        except Error as e:
            print("Error while initializing cache: " + str(e))

    def _get(self, request: Request) -> tuple[str, datetime] | None:
        """
        Get the response and timestamp from the cache
        :param request: The request to get the response for
        :return:  A tuple containing the response and timestamp
        """
        if not self.initialized:
            return None

        headers = json.dumps(request.headers) if request.headers else ""
        data = json.dumps(request.data) if request.data else ""
        try:
            with self.connect() as conn:
                c = conn.cursor()
                c.execute(
                    "SELECT response, timestamp FROM cache WHERE method = ? "
                    "AND url = ? AND body = ? AND headers = ? AND data = ?",
                    (request.method, request.url, request.body, headers, data))
                result = c.fetchone()

                if not result:
                    return None

                time_stamp = datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S")

                return str(result[0]), time_stamp
        except Exception as e:
            print("Error while fetching from cache: " + str(e))

        return None

    def get(self, request: Request) -> str | None:
        cached = self._get(request)

        if not cached:
            return None

        response, timestamp = cached

        time_diff = datetime.now() - timestamp

        if 0 < request.max_age < time_diff.seconds:
            return None

        return response

    def set(self, request: Request, response: str) -> None:
        if not self.initialized:
            return

        exists = self._get(request) is not None

        headers = json.dumps(request.headers) if request.headers else ""
        data = json.dumps(request.data) if request.data else ""
        try:
            with self.connect() as conn:
                if exists:
                    c = conn.cursor()

                    c.execute("UPDATE cache SET response = ?, timestamp = ? WHERE method = ? "
                              "AND url = ? AND body = ? AND headers = ? AND data = ?",
                              (response, _get_current_timestamp(), request.method, request.url, request.body, headers,
                               data))
                    conn.commit()
                    return
                else:
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO cache (method, url, response, body, headers, data, timestamp) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (request.method, request.url, response, request.body, headers, data, _get_current_timestamp()))
                    conn.commit()
        except Error as e:
            print("Error while saving to cache: " + str(e))
