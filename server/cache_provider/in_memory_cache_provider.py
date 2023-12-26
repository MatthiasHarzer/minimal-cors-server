import json
from datetime import datetime

from server.cache_provider.base_cache_provider import CacheProvider
from server.request import Request


def _hash_request(request: Request) -> int:
    """
    Hash a request
    :param request:
    :return:
    """
    return hash((request.method, request.url, request.body, json.dumps(request.headers), json.dumps(request.data),
                 request.cache))


class InMemoryCacheProvider(CacheProvider):
    def __init__(self):
        self.cache: dict[int, tuple[str, datetime]] = {}

    def _get(self, request: Request) -> tuple[str, datetime] | None:
        hashed = _hash_request(request)
        return self.cache.get(hashed)

    def set(self, request: Request, response: str) -> None:
        hashed = _hash_request(request)
        self.cache[hashed] = (response, datetime.now())
