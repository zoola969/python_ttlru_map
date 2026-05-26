from __future__ import annotations

from collections.abc import Hashable
from typing import Any, Generic, TypeVar

_TKey = TypeVar("_TKey", bound=Hashable)
_TValue = TypeVar("_TValue")


class _BaseMap(Generic[_TKey, _TValue]):
    __slots__ = ("_dict",)

    def __init__(self) -> None:
        self._dict: dict[_TKey, Any] = {}
