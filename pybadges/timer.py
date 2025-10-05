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
import time
import typing as t
from datetime import timedelta


class Timer:
    def __init__(self):
        self._start = None
        self._stop = None

    def start(self) -> int:
        self._start = time.process_time_ns()
        return self._start

    def stop(self) -> int:
        self._stop = time.process_time_ns()
        return self._stop

    @property
    def dt(self) -> int | None:
        if self._start is None or self._stop is None:
            return None
        return self._stop - self._start

    def in_nanoseconds(self) -> int | None:
        return self.dt

    def in_seconds(self) -> float | None:
        dt = self.dt
        if dt is None:
            return None
        seconds = dt / 1_000_000_000
        return seconds

    def in_timedelta(self) -> timedelta | None:
        seconds = self.in_seconds()
        if seconds is None:
            return None
        return timedelta(seconds=seconds)

    def __enter__(self) -> t.Self:
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()
