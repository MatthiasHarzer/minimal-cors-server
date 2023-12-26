import json
from datetime import datetime

from server.cache_provider.base_cache_provider import CacheProvider
from server.request import Request
import mysql.connector
import mysql.connector.cursor

_TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS cache (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    method TEXT NOT NULL,
    url TEXT NOT NULL,
    response TEXT NOT NULL,
    body TEXT NULL,
    headers TEXT NULL,
    data TEXT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );"""


def _get_current_timestamp() -> str:
    """
    Get the current timestamp as a string
    :return:
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class MySQLCacheProvider(CacheProvider):
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.initialized = False
        try:
            self._create_table()
            self.initialized = True
        except mysql.connector.errors.Error as e:
            print("Error while initializing cache: " + str(e))

    def _connect(self) -> mysql.connector.MySQLConnection:
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def _create_table(self):
        db = self._connect()
        try:
            c = db.cursor()
            c.execute(_TABLE_SQL)
            db.commit()
        except mysql.connector.errors.Error as e:
            print(e)

    def _get(self, request: Request) -> tuple[str, datetime] | None:
        """
        Get the response and timestamp from the cache
        :param request: The request to get the response for
        :return:  A tuple containing the response and timestamp
        """

        headers = json.dumps(request.headers) if request.headers else ""
        data = json.dumps(request.data) if request.data else ""

        db = self._connect()
        c = db.cursor()
        c.execute(
            "SELECT response, timestamp FROM cache WHERE method = %s AND url = %s AND body <=> %s AND headers <=> %s AND data <=> %s",
            (request.method, request.url, request.body, headers, data))

        result = c.fetchone()
        if result:
            return result[0], result[1]
        return None

    def set(self, request: Request, response: str) -> None:
        """
        Save the response to the cache
        :param request: The request to save the response for
        :param response: The response to save
        :return:
        """
        headers = json.dumps(request.headers) if request.headers else ""
        data = json.dumps(request.data) if request.data else ""

        db = self._connect()
        c = db.cursor()
        c.execute(
            "SELECT id FROM cache WHERE method = %s AND url = %s AND body <=> %s AND headers <=> %s AND data <=> %s",
            (request.method, request.url, request.body, headers, data))
        existing = c.fetchone()

        if existing:
            c.execute("UPDATE cache SET response = %s, timestamp = %s WHERE id = %s",
                      (response, _get_current_timestamp(), existing[0]))
        else:
            c.execute(
                "INSERT INTO cache (method, url, response, body, headers, data, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (request.method, request.url, response, request.body, headers, data, _get_current_timestamp()))

        db.commit()
