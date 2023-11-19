import time
from collections import deque
from collections.abc import Iterator, MutableMapping
from datetime import timedelta
from threading import Lock
from typing import Deque, Generic, Hashable, NamedTuple, TypeVar

_K = TypeVar("_K", bound=Hashable)
_V = TypeVar("_V")


class _DequeKey(Generic[_K], NamedTuple):
    time_: float
    key: _K


class _TTLDictValue(Generic[_V], NamedTuple):
    value: _V
    time_: float


class TTLDict(MutableMapping[_K, _V]):
    def __init__(self, max_size: int, ttl: timedelta):
        self._dict: dict[_K, _TTLDictValue[_V]] = {}
        self._deque: Deque[_DequeKey[_K]] = deque()
        self._max_size = max_size
        self._ttl = ttl
        self._lock = Lock()

    def _update_by_ttl(self, current_time: float | None = None) -> None:
        current_time = current_time if current_time is not None else time.time()
        while len(self._deque) > 0:
            item = self._deque[0]
            if item.time_ + self._ttl.total_seconds() >= current_time:
                break
            else:
                self._deque.popleft()
                self._dict.pop(item.key, None)

    def _update_by_size(self) -> None:
        while len(self._deque) > self._max_size:
            item = self._deque.popleft()
            self._dict.pop(item.key, None)

    def __setitem__(self, __key: _K, __value: _V) -> None:
        with self._lock:
            time_ = time.time()
            self._dict[__key] = _TTLDictValue(value=__value, time_=time_)
            self._deque.append(_DequeKey(time_=time_, key=__key))
            self._update_by_ttl(current_time=time_)
            self._update_by_size()

    def __delitem__(self, __key: _K) -> None:
        with self._lock:
            self._dict.pop(__key, None)
            self._update_by_ttl()

    def __getitem__(self, __key: _K) -> _V:
        with self._lock:
            self._update_by_ttl()
            return self._dict[__key].value

    def __len__(self) -> int:
        with self._lock:
            self._update_by_ttl()
            return len(self._dict)

    def __iter__(self) -> Iterator[_K]:
        return iter(self._dict)


def hui(size: int) -> str:
    """Return hui

    :param size: size of hui
    :return: hui
    """
    return "hui"
