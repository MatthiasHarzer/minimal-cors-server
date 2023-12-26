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
    cache_type = os.environ.get("CACHE", "sqlite")

    match cache_type:
        case "sqlite":
            return SQLiteCacheProvider(CACHE_DB_FILE)
        case "memory":
            return InMemoryCacheProvider()

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
    cached = cache.get(request)

    if request.cache and cached:
        return cached

    req_text = fetch(request)
    if request.cache and not cached:
        cache.set(request, req_text)

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
