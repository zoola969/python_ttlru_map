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
    __slots__ = (
        "_dict",
        "_deque",
        "_max_size",
        "_ttl",
        "_update_ttl_on_get",
        "_lock",
    )

    def __init__(
        self,
        *,
        ttl: timedelta,
        max_size: int = 0,
        update_ttl_on_get: bool = True,
    ):
        """A dictionary that removes items after a certain time.

        :param max_size: the maximum number of items in the dictionary. 0 means no limit.
        :param ttl: the time to live for each item in the dictionary.
        :param update_ttl_on_get: whether to update the time to live when getting an item.
        """
        self._dict: dict[_K, _TTLDictValue[_V]] = {}
        self._deque: Deque[_DequeKey[_K]] = deque()
        self._max_size = max_size
        self._ttl = ttl
        self._update_ttl_on_get = update_ttl_on_get
        self._lock = Lock()

    def _update_by_ttl(self, current_time: float | None = None) -> None:
        """Remove items that have expired."""
        current_time = current_time if current_time is not None else time.time()
        while len(self._deque) > 0:
            latest_item = self._deque[0]
            if latest_item.time_ + self._ttl.total_seconds() >= current_time:
                break
            else:
                self._deque.popleft()
                self._delitem(latest_item.key, time_=latest_item.time_)

    def _update_by_size(self) -> None:
        """Remove the oldest items that exceed the maximum size."""
        while len(self._dict) > self._max_size:
            latest_item = self._deque.popleft()
            self._delitem(latest_item.key, time_=latest_item.time_)

    def _setitem(self, __key: _K, __value: _V, time_: float) -> None:
        self._dict[__key] = _TTLDictValue(value=__value, time_=time_)
        self._deque.append(_DequeKey(time_=time_, key=__key))

    def _delitem(self, __key: _K, time_: float) -> None:
        item = self._dict.get(__key, None)
        if item is not None and item.time_ == time_:
            self._dict.pop(__key, None)

    def __setitem__(self, __key: _K, __value: _V) -> None:
        with self._lock:
            time_ = time.time()
            self._setitem(__key, __value, time_)
            self._update_by_ttl(current_time=time_)
            if self._max_size > 0:
                self._update_by_size()

    def __delitem__(self, __key: _K) -> None:
        with self._lock:
            self._dict.pop(__key, None)
            self._update_by_ttl()

    def __getitem__(self, __key: _K) -> _V:
        with self._lock:
            time_ = time.time()
            self._update_by_ttl(current_time=time_)
            item = self._dict[__key].value
            if self._update_ttl_on_get:
                self._setitem(__key, item, time_)
            return item

    def __len__(self) -> int:
        with self._lock:
            self._update_by_ttl()
            return len(self._dict)

    def __iter__(self) -> Iterator[_K]:
        return iter(self._dict)
