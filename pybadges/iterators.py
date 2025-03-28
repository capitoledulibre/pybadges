# Copyright 2025 Toulibre
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
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
