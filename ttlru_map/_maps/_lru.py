from collections.abc import Hashable, Iterator, MutableMapping
from dataclasses import dataclass
from threading import Lock
from typing import Any, Generic, TypeVar

from typing_extensions import override

from ttlru_map._exceptions import TTLMapInvalidConfigError
from ttlru_map._linked_list import DoubleLinkedListNode

_TKey = TypeVar("_TKey", bound=Hashable)
_TValue = TypeVar("_TValue")

_MISSING: Any = object()


@dataclass(frozen=True)
class _DictValue(Generic[_TKey, _TValue]):
    __slots__ = ("node", "value")
    node: DoubleLinkedListNode[_TKey]
    value: _TValue

    @override
    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.__class__.__name__}(node={self.node}, value={self.value})"


class LruMap(MutableMapping[_TKey, _TValue], Generic[_TKey, _TValue]):
    def __init__(self, max_size: int) -> None:
        if type(max_size) is not int or max_size <= 0:
            msg = "max_size must be a positive int"
            raise TTLMapInvalidConfigError(msg)
        self._dict: dict[_TKey, _DictValue[_TKey, _TValue]] = {}
        self._ll_head: DoubleLinkedListNode[_TKey] | None = None
        self._ll_tail: DoubleLinkedListNode[_TKey] | None = None
        self._max_size = max_size
        self._lock = Lock()

    def _pop_ll_node(self, node: DoubleLinkedListNode[_TKey]) -> None:
        """Pop a node from the linked list."""
        if node is self._ll_head:
            self._ll_head = node.next
        if node is self._ll_tail:
            self._ll_tail = node.prev

        if node.next is not None:
            node.next.prev = node.prev
        if node.prev is not None:
            node.prev.next = node.next
        node.next = None
        node.prev = None

    def _put_node_to_end(self, node: DoubleLinkedListNode[_TKey]) -> None:
        """Put a node to the end of the linked list."""
        if self._ll_tail is None:
            self._ll_head = node
            self._ll_tail = node
        else:
            self._ll_tail.next = node
            node.prev = self._ll_tail
            self._ll_tail = node

    def _setitem(self, __key: _TKey, __value: _TValue, /) -> None:
        """Set an item in the dictionary and put it to the end of the linked list."""
        new_node = DoubleLinkedListNode(value=__key)

        if (item := self._dict.get(__key, None)) is not None:
            self._pop_ll_node(item.node)

        self._put_node_to_end(new_node)
        self._dict[__key] = _DictValue(value=__value, node=new_node)

    def _delitem(self, item: _DictValue[_TKey, _TValue]) -> None:
        """Delete an item from the dictionary and the linked list."""
        del self._dict[item.node.value]
        self._pop_ll_node(item.node)

    def _update_by_size(self) -> None:
        """Remove the oldest items that exceed the maximum size."""
        while len(self._dict) > self._max_size and self._ll_head is not None:
            del self._dict[self._ll_head.value]
            self._pop_ll_node(self._ll_head)

    @override
    def __setitem__(self, __key: _TKey, __value: _TValue, /) -> None:
        with self._lock:
            self._setitem(__key, __value)
            self._update_by_size()

    @override
    def __delitem__(self, __key: _TKey, /) -> None:
        with self._lock:
            item = self._dict[__key]
            self._delitem(item)

    @override
    def __getitem__(self, __key: _TKey, /) -> _TValue:
        with self._lock:
            item = self._dict[__key].value
            self._setitem(__key, item)
            return item

    @override
    def __len__(self) -> int:
        with self._lock:
            return len(self._dict)

    @override
    def __iter__(self) -> Iterator[_TKey]:
        return iter(self._dict)

    @override
    def __contains__(self, key: object) -> bool:
        with self._lock:
            return key in self._dict

    @override
    def get(self, key: _TKey, default: Any = None) -> Any:
        """Return value without promoting the key. Returns ``default`` if missing."""
        with self._lock:
            item = self._dict.get(key)
            if item is None:
                return default
            return item.value

    @override
    def pop(self, key: _TKey, default: Any = _MISSING) -> Any:
        """Atomically remove ``key`` and return its value, or ``default`` if missing."""
        with self._lock:
            item = self._dict.get(key)
            if item is None:
                if default is _MISSING:
                    raise KeyError(key)
                return default
            self._delitem(item)
            return item.value

    @override
    def popitem(self) -> tuple[_TKey, _TValue]:
        """Atomically remove and return the least-recently-used (head) item."""
        with self._lock:
            head = self._ll_head
            if head is None:
                msg = "LruMap is empty"
                raise KeyError(msg)
            key = head.value
            item = self._dict[key]
            self._delitem(item)
            return key, item.value
