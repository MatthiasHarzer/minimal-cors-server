from typing import Literal

from pydantic import BaseModel, Field

RequestMethod = Literal["GET", "POST", "PUT", "DELETE"]


class Request(BaseModel):
    method: RequestMethod
    """The HTTP method to use for the request."""

    url: str | None = None
    """The URL to send the request to."""

    body: str | None = ""
    """The body of the request."""

    headers: dict | None = Field(default_factory=dict)
    """The headers to send with the request."""

    data: dict | None = Field(default_factory=dict)
    """The data to send with the request. (e.g. form data)"""

    cache: bool = False
    """Whether or not to cache the response."""

    max_age: int = 0
    """The maximum age of the cached response in seconds."""
