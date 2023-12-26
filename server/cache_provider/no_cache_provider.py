from server.main import CacheProvider
from server.request import Request


class NoCacheProvider(CacheProvider):
    def _get(self, request: Request) -> str | None:
        pass

    def set(self, request: Request, response: str) -> None:
        pass
