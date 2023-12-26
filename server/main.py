import os
from typing import Protocol

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.requests import Request as FastApiRequest
from fastapi.responses import PlainTextResponse

from server.cache_provider.base_cache_provider import CacheProvider
from server.cache_provider.in_memory_cache_provider import InMemoryCacheProvider
from server.cache_provider.mysql_cache_provider import MySQLCacheProvider
from server.cache_provider.no_cache_provider import NoCacheProvider
from server.cache_provider.sqlite_cache_provider import SQLiteCacheProvider
from server.request import Request

CACHE_DB_FILE = "cache.db"

app = FastAPI()

app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_cache_provider() -> CacheProvider:
    cache_type = os.environ.get("CACHE_MODE", "sqlite")

    match cache_type:
        case "sqlite":
            db_file = os.environ.get("SQLITE_FILE", CACHE_DB_FILE)
            return SQLiteCacheProvider(db_file)
        case "memory":
            return InMemoryCacheProvider()
        case "mysql":
            host = os.environ.get("MYSQL_HOST")
            user = os.environ.get("MYSQL_USER")
            password = os.environ.get("MYSQL_PASSWORD")
            database = os.environ.get("MYSQL_DATABASE")
            port = os.environ.get("MYSQL_PORT", 3306)

            if None in (host, user, password, database):
                print("WARNING: Missing environment variables for MySQL cache provider. "
                      "Required: MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE"
                      "\nFalling back to NoCacheProvider.")
                return NoCacheProvider()

            return MySQLCacheProvider(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
        case "none":
            return NoCacheProvider()

    print(f"WARNING: No cache provider found for type {cache_type}. Using NoCacheProvider.")

    return NoCacheProvider()


cache: CacheProvider = get_cache_provider()


def fetch(request: Request):
    req = requests.request(request.method, request.url,
                           data=request.data,
                           headers=request.headers,
                           json=request.body)
    return req.text


def handle_fetch(request: Request) -> str:
    try:
        cached = cache.get(request)
    except Exception as e:
        print(f"Error while getting from cache: {e}")
        cached = None

    if request.cache and cached:
        return cached

    req_text = fetch(request)
    if request.cache and not cached:
        try:
            cache.set(request, req_text)
        except Exception as e:
            print(f"Error while setting cache: {e}")

    return req_text


@app.post("/{_:path}")
def handle_request(request: Request, meta: FastApiRequest):
    try:
        result = handle_fetch(request)
        return PlainTextResponse(result)
    except requests.exceptions.ConnectionError as e:
        return PlainTextResponse("Connection error", status_code=400)
    except (requests.exceptions.InvalidURL, requests.exceptions.MissingSchema) as e:
        return PlainTextResponse(str(e), status_code=400)
    except Exception as e:
        return PlainTextResponse(str(e), status_code=500)
