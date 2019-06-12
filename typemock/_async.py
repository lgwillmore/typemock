from typing import Awaitable, Any, Iterator


class SimpleResponseAwaitable(Awaitable):

    def __init__(self, response: Any):
        self._response = response

    def __await__(self) -> Iterator[Any]:
        yield self._response
