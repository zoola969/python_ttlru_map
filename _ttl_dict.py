import time
from collections import deque
from collections.abc import MutableMapping, Iterator
from datetime import timedelta
from threading import Lock
from typing import Generic, TypeVar, Hashable, Deque, NamedTuple

_K = TypeVar("_K", bound=Hashable)
_V = TypeVar("_V")


class _DequeKey(Generic[_K], NamedTuple):
    time_: float
    key: _K


class TTLDict(Generic[_K, _V], MutableMapping):
    def __init__(self, max_size: int, ttl: timedelta):
        self._dict: dict[_K, _V] = {}
        self._deque: Deque[_DequeKey] = deque()
        self._max_size = max_size
        self._ttl = ttl
        self._lock = Lock()

    def _update_by_ttl(self) -> None:
        current_time = time.time()
        while len(self._deque) > 0:
            item = self._deque[0]
            if item.time_ + self._ttl.total_seconds() >= current_time:
                break
            else:
                self._deque.popleft()
                del self._dict[item.key]

    def _update_by_size(self) -> None:
        while len(self._deque) > self._max_size:
            item = self._deque.popleft()
            del self._dict[item.key]

    def _del_key_from_deque(self, key__: _K) -> None:
        for item in self._deque:
            if item.key == key__:
                self._deque.remove(item)
                return None

    def __setitem__(self, __key: _K, __value: _V) -> None:
        with self._lock:
            self._dict[__key] = __value
            self._deque.append(_DequeKey(time_=time.time(), key=__key))
            self._update_by_ttl()
            self._update_by_size()

    def __delitem__(self, __key: _K) -> None:
        with self._lock:
            self._del_key_from_deque(__key)
            self._dict.pop(__key, None)
            self._update_by_ttl()

    def __getitem__(self, __key: _K) -> _V:
        with self._lock:
            self._update_by_ttl()
            return self._dict[__key]

    def __len__(self) -> int:
        with self._lock:
            self._update_by_ttl()
            return len(self._dict)

    def __iter__(self) -> Iterator[_K]:
        return iter(self._dict)
