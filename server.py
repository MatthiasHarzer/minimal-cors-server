from typing import Literal

import requests
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse

from cache import Cache
from request import Request

CACHE_DB_FILE = "./cache.db"

origins = [
    "*"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def fetch(request: Request):
    req = requests.request(request.method, request.url, data=request.data, headers=request.headers, json=request.body)
    return req.text


@app.post("/request")
def handle_request(request: Request):
    cache = Cache(CACHE_DB_FILE)
    cached = cache.get(request)

    if request.cache and cached:
        return PlainTextResponse(cached)

    req = requests.request(request.method, request.url, data=request.data, headers=request.headers, json=request.body)
    if request.cache and not cached:
        cache.set(request, req.text)

    return PlainTextResponse(req.text)
