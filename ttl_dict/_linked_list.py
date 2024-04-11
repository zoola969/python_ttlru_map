from typing import Generic, Optional, TypeGuard, TypeVar

_T = TypeVar("_T")


class DoubleLinkedListNode(Generic[_T]):

    __slots__ = (
        "_value",
        "next",
        "prev",
    )

    def __init__(self, value: _T):
        self._value = value
        self.next: Optional["DoubleLinkedListNode"] = None
        self.prev: Optional["DoubleLinkedListNode"] = None

    @property
    def value(self) -> _T:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DoubleLinkedListNode):
            return False
        if self is other:
            return True
        if not tg(self, type(self._value)):
            return False
        return self._value == other._value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self._value})"


def tg(value: DoubleLinkedListNode[_T], type_: type[_T]) -> TypeGuard[DoubleLinkedListNode[_T]]:
    return type(value.value) is type_
