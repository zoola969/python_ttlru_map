from typing import Generic, Optional, TypeVar

_T = TypeVar("_T")


class DoubleLinkedListNode(Generic[_T]):

    __slots__ = (
        "_value",
        "next",
        "prev",
    )

    def __init__(self, value: _T):
        self._value = value
        self.next: Optional["DoubleLinkedListNode[_T]"] = None
        self.prev: Optional["DoubleLinkedListNode[_T]"] = None

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
