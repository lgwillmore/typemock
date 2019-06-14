from typing import Awaitable, Any, Generator


class SimpleResponseAwaitable(Awaitable):

    def __init__(self, response: Any):
        self._response = response

    def __await__(self) -> Generator[Any, Any, Any]:
        yield self._response
