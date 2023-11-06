from typing import Iterator
from typing import TypeVar


T = TypeVar("T")


class PeekableIterator(Iterator[T]):
    def __init__(self, iterator: Iterator) -> None:
        self._inner = iterator
        self._buffer = []

    def empty(self) -> bool:
        if self._buffer:
            return False
        try:
            self._buffer.append(next(self._inner))
            return False
        except StopIteration:
            return True

    def peek(self) -> T:
        if not self._buffer:
            self._buffer.append(next(self._inner))

        return self._buffer[0]

    def __next__(self) -> T:
        if self._buffer:
            return self._buffer.pop(0)
        else:
            return self._inner.__next__()


def peekable(it: Iterator) -> PeekableIterator:
    return PeekableIterator(it)
