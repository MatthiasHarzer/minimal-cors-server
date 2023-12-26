import json
import sqlite3
from datetime import datetime
from sqlite3 import Error

from server.request import Request

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


def _get_current_timestamp() -> str:
    """
    Get the current timestamp as a string
    :return:
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class SQLiteCacheProvider:
    """
    A cache provider that uses SQLite as the backend
    """

    def __init__(self, file_name: str):
        self.db_file = file_name
        self.initialized = False
        try:
            self._create_table()
            self.initialized = True
        except Error as e:
            print("Error while initializing cache: " + str(e))

    def _create_table(self):
        try:
            c = self._connect().cursor()
            c.execute(_TABLE_SQL)
        except Error as e:
            print(e)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_file)

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
            with self._connect() as conn:
                c = conn.cursor()
                c.execute(
                    "SELECT response, timestamp FROM cache WHERE method = ? "
                    "AND url = ? AND body IS ? AND headers IS ? AND data IS ?",
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

        if request.max_age <= 0 or 0 < time_diff.seconds < request.max_age:
            return response

        return None

    def set(self, request: Request, response: str) -> None:
        if not self.initialized:
            return

        headers = json.dumps(request.headers) if request.headers else ""
        data = json.dumps(request.data) if request.data else ""
        try:
            with self._connect() as conn:
                c = conn.cursor()

                c.execute("SELECT response, timestamp FROM cache WHERE method = ? "
                          "AND url = ? AND body IS ? AND headers IS ? AND data IS ?",
                          (request.method, request.url, request.body, headers, data))
                has_existing = c.fetchone() is not None

                if has_existing:
                    c.execute("UPDATE cache SET response = ?, timestamp = ? WHERE method = ? "
                              "AND url = ? AND body IS ? AND headers IS ? AND data IS ?",
                              (response, _get_current_timestamp(), request.method, request.url, request.body, headers,
                               data))
                    conn.commit()
                    return
                else:
                    c.execute(
                        "INSERT INTO cache (method, url, response, body, headers, data, timestamp) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (request.method, request.url, response, request.body, headers, data, _get_current_timestamp()))
                    conn.commit()
        except Error as e:
            print("Error while saving to cache: " + str(e))
