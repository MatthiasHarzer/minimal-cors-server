from typing import Literal

import requests
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import PlainTextResponse

app = FastAPI()

RequestMethod = Literal["GET", "POST", "PUT", "DELETE"]


class Request(BaseModel):
    method: RequestMethod
    url: str
    body: str | None = None
    headers: dict | None = None
    data: dict | None = None
    # cache: bool = False


@app.post("/request")
def handle_request(request: Request):
    req = requests.request(request.method, request.url, data=request.data, headers=request.headers, json=request.body)
    return PlainTextResponse(req.text)
