import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.requests import Request as FastApiRequest
from fastapi.responses import PlainTextResponse

from cache import Cache
from request import Request

CACHE_DB_FILE = "./cache.db"

origins = [
    "*"
]

app = FastAPI()

app.add_middleware(GZipMiddleware)
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


def handle_fetch(request: Request) -> str:
    cache = Cache(CACHE_DB_FILE)
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
