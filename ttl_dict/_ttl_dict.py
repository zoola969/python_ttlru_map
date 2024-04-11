import time
from collections.abc import Hashable
from dataclasses import dataclass
from datetime import timedelta
from threading import Lock
from typing import Generic, Iterator, MutableMapping, Optional, TypeVar

from ttl_dict._exceptions import TTLDictInvalidConfigError
from ttl_dict._linked_list import DoubleLinkedListNode

_TKey = TypeVar("_TKey", bound=Hashable)
_TValue = TypeVar("_TValue")


@dataclass(frozen=True, slots=True)
class _LinkedListValue(Generic[_TKey]):
    time_: float
    key: _TKey

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.__class__.__name__}(time_={self.time_}, key={self.key})"


@dataclass(frozen=True, slots=True)
class _DictValue(Generic[_TKey, _TValue]):
    node: DoubleLinkedListNode[_LinkedListValue[_TKey]]
    value: _TValue

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.__class__.__name__}(node={self.node}, value={self.value})"


class TTLDict(MutableMapping[_TKey, _TValue]):
    __slots__ = (
        "_dict",
        "_ll_end",
        "_ll_head",
        "_lock",
        "_max_size",
        "_ttl",
        "_update_ttl_on_get",
    )

    def __init__(
        self,
        *,
        ttl: Optional[timedelta],
        max_size: Optional[int] = None,
        update_ttl_on_get: bool = False,
    ):
        """A dictionary that removes items after a certain time.

        :param max_size: the maximum number of items in the dictionary. 0 means no limit.
        :param ttl: the time to live for each item in the dictionary.
        :param update_ttl_on_get: whether to update the time to live when getting an item.
        """
        self._validate_config(max_size, ttl, update_ttl_on_get)
        self._dict: dict[_TKey, _DictValue[_TKey, _TValue]] = {}
        self._ll_head: Optional[DoubleLinkedListNode[_LinkedListValue[_TKey]]] = None
        self._ll_end: Optional[DoubleLinkedListNode[_LinkedListValue[_TKey]]] = None
        self._max_size = max_size
        self._ttl = ttl
        self._update_ttl_on_get = update_ttl_on_get
        self._lock = Lock()

    def _validate_config(
        self,
        max_size: Optional[int],
        ttl: Optional[timedelta],
        update_ttl_on_get: bool,
    ) -> None:
        if max_size is None and ttl is None:
            raise TTLDictInvalidConfigError("max_size and ttl cannot be None at the same time.")
        if max_size is not None and max_size <= 0:
            raise TTLDictInvalidConfigError("max_size must be greater than 0.")
        if ttl is not None and ttl.total_seconds() <= 0:
            raise TTLDictInvalidConfigError("ttl must be greater than 0.")
        if ttl is None and update_ttl_on_get:
            raise TTLDictInvalidConfigError("update_ttl_on_get cannot be True when ttl is None.")

    def _update_by_ttl(self, current_time: Optional[float] = None) -> None:
        """Remove items that have expired."""
        if self._ttl is None:
            return
        current_time = current_time if current_time is not None else time.time()
        while self._ll_head is not None:
            if self._ll_head.value.time_ + self._ttl.total_seconds() >= current_time:
                break
            del self._dict[self._ll_head.value.key]
            self._pop_ll_node(self._ll_head)

    def _update_by_size(self) -> None:
        """Remove the oldest items that exceed the maximum size."""
        if self._max_size is None:
            return
        while len(self._dict) > self._max_size and self._ll_head is not None:
            del self._dict[self._ll_head.value.key]
            self._pop_ll_node(self._ll_head)

    def _pop_ll_node(self, node: DoubleLinkedListNode[_LinkedListValue[_TKey]]) -> None:
        """Pop a node from the linked list."""
        if node is self._ll_head:
            self._ll_head = node.next
        if node is self._ll_end:
            self._ll_end = node.prev

        if node.next is not None:
            node.next.prev = node.prev
        if node.prev is not None:
            node.prev.next = node.next
        node.next = None
        node.prev = None

    def _put_node_to_end(self, node: DoubleLinkedListNode[_LinkedListValue[_TKey]]) -> None:
        """Put a node to the end of the linked list."""
        if self._ll_end is None:
            self._ll_head = node
            self._ll_end = node
        else:
            self._ll_end.next = node
            node.prev = self._ll_end
            self._ll_end = node

    def _setitem(self, __key: _TKey, __value: _TValue, time_: float) -> None:
        """Set an item in the dictionary and put it to the end of the linked list."""
        new_node = DoubleLinkedListNode(value=_LinkedListValue(time_=time_, key=__key))

        if (item := self._dict.get(__key, None)) is not None:
            self._pop_ll_node(item.node)
            self._put_node_to_end(new_node)
        else:
            self._put_node_to_end(new_node)

        self._dict[__key] = _DictValue(value=__value, node=new_node)

    def _delitem(self, item: _DictValue[_TKey, _TValue]) -> None:
        """Delete an item from the dictionary and the linked list."""
        del self._dict[item.node.value.key]
        self._pop_ll_node(item.node)

    def __setitem__(self, __key: _TKey, __value: _TValue) -> None:
        with self._lock:
            time_ = time.time()
            self._setitem(__key, __value, time_)
            self._update_by_ttl(current_time=time_)
            self._update_by_size()

    def __delitem__(self, __key: _TKey) -> None:
        with self._lock:
            item = self._dict[__key]
            self._delitem(item)
            self._update_by_ttl()

    def __getitem__(self, __key: _TKey) -> _TValue:
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

    def __iter__(self) -> Iterator[_TKey]:
        return iter(self._dict)
