from typing import Literal

from pydantic import BaseModel, Field

RequestMethod = Literal["GET", "POST", "PUT", "DELETE"]


class Request(BaseModel):
    method: RequestMethod
    url: str
    body: str | None = ""
    headers: dict | None = Field(default_factory=dict)
    data: dict | None = Field(default_factory=dict)
    cache: bool = False
