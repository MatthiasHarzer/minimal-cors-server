from typing import Literal

import requests
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import PlainTextResponse

app = FastAPI()

RequestType = Literal["GET", "POST", "PUT", "DELETE"]


class Request(BaseModel):
    type: RequestType
    url: str
    body: str | None = None
    headers: dict | None = None
    data: dict | None = None
    # cache: bool = False


@app.post("/request")
def handle_request(request: Request):
    req = requests.request(request.type, request.url, data=request.data, headers=request.headers, json=request.body)
    return PlainTextResponse(req.text)
