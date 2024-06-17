from datetime import timedelta
from unittest.mock import patch

import pytest

from tests.utils import LockMock
from ttlru_map import TTLMap
from ttlru_map._linked_list import DoubleLinkedListNode
from ttlru_map._ttl_map import _DictValue, _LinkedListValue


def test_delete():
    d = TTLMap(ttl=timedelta(seconds=1000))
    lock_mock = LockMock()
    d._lock = lock_mock
    key = 1
    value = 2
    time_ = 10

    node = DoubleLinkedListNode(value=_LinkedListValue(time_=time_, key=key))
    item = _DictValue(node=node, value=value)
    d._dict[key] = item
    d._ll_head = node
    d._ll_end = node

    with patch.object(TTLMap, "_delitem", wraps=d._delitem) as delitem_mock, patch.object(
        TTLMap,
        "_update_by_ttl",
        wraps=d._update_by_ttl,
    ) as update_by_ttl_mock:
        del d[key]
        assert d._dict == {}
        assert d._ll_head is None
        assert d._ll_end is None

        delitem_mock.assert_called_once_with(item)
        update_by_ttl_mock.assert_called_once_with()


def test_delete__item_not_found():
    d = TTLMap(ttl=timedelta(seconds=1000))

    with pytest.raises(KeyError):
        del d[1]


def test_delete__item_expired():
    ttl = timedelta(seconds=100)
    d = TTLMap(ttl=ttl)
    key = 1
    value = 2
    time_ = 10

    node = DoubleLinkedListNode(value=_LinkedListValue(time_=time_, key=key))
    d._dict[key] = _DictValue(node=node, value=value)
    d._ll_head = node
    d._ll_end = node

    del d[key]
    assert d._dict == {}
    assert d._ll_head is None
    assert d._ll_end is None
