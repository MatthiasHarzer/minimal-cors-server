from server.request import Request


class NoCacheProvider:
    def get(self, request: Request) -> str | None:
        pass

    def set(self, request: Request, response: str) -> None:
        pass
