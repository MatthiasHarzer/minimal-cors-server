from abc import ABC, abstractmethod
from datetime import datetime

from server.request import Request


class CacheProvider(ABC):
    """
    A cache provider that can be used to cache requests
    """

    @abstractmethod
    def _get(self, request: Request) -> tuple[str, datetime] | None:
        """
        Get the response and timestamp from the cache
        :param request: The request to get the response for
        :return:  A tuple containing the response and timestamp
        """

    def get(self, request: Request) -> str | None:
        """
        Get the response from the cache if it exists and is not stale
        :param request: The request to get the response for
        :return: The response if it exists and is not stale, None otherwise
        """
        cached = self._get(request)
        if not cached:
            return None

        response, timestamp = cached

        time_diff = datetime.now() - timestamp

        if request.max_age <= 0 or 0 < time_diff.seconds < request.max_age:
            return response

        return None

    @abstractmethod
    def set(self, request: Request, response: str) -> None:
        """
        Save the response to the cache
        :param request: The request to save the response for
        :param response: The response to save
        :return:
        """
