from __future__ import annotations

from typing import Generic, TypeVar

_T = TypeVar("_T")


class DoubleLinkedListNode(Generic[_T]):

    __slots__ = (
        "_value",
        "next",
        "prev",
    )

    def __init__(self, value: _T) -> None:
        self._value = value
        self.next: DoubleLinkedListNode[_T] | None = None
        self.prev: DoubleLinkedListNode[_T] | None = None

    @property
    def value(self) -> _T:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DoubleLinkedListNode):
            return False
        if self is other:
            return True
        return self._value == other._value  # type: ignore[no-any-return]

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.__class__.__name__}(value={self._value})"
