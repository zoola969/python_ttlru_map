from datetime import timedelta
from unittest.mock import patch

import pytest

from tests.utils import LockMock
from ttlru_map import TTLMap
from ttlru_map._ttl_map import DoubleLinkedListNode, _DictValue, _LinkedListValue


@pytest.mark.parametrize("update_ttl_on_get", [True, False])
def test_get(update_ttl_on_get: bool):
    d = TTLMap(ttl=timedelta(seconds=1000), update_ttl_on_get=update_ttl_on_get)
    lock_mock = LockMock()
    d._lock = lock_mock
    key = 1
    value = 2
    time_ = 10

    node = DoubleLinkedListNode(value=_LinkedListValue(time_=time_, key=key))
    d._dict[key] = _DictValue(node=node, value=value)
    d._ll_head = node
    d._ll_end = node

    with patch("time.time", return_value=time_) as time_mock, patch.object(
        TTLMap,
        "_setitem",
        wraps=d._setitem,
    ) as setitem_mock, patch.object(TTLMap, "_update_by_ttl", wraps=d._update_by_ttl) as update_by_ttl_mock:
        assert d[key] == value
        time_mock.assert_called_once()
        update_by_ttl_mock.assert_called_once_with(current_time=time_)
        if update_ttl_on_get:
            setitem_mock.assert_called_once_with(key, value, time_)
        else:
            setitem_mock.assert_not_called()


def test_get__item_not_found():
    d = TTLMap(ttl=timedelta(seconds=1000))

    with pytest.raises(KeyError):
        _ = d[1]


def test_get__item_expired():
    ttl = timedelta(seconds=100)
    d = TTLMap(ttl=ttl)
    key = 1
    value = 2
    time_ = 10

    node = DoubleLinkedListNode(value=_LinkedListValue(time_=time_, key=key))
    d._dict[key] = _DictValue(node=node, value=value)
    d._ll_head = node
    d._ll_end = node

    with patch("time.time", return_value=time_ + ttl.total_seconds() + 1):  # noqa: SIM117
        with pytest.raises(KeyError):
            _ = d[key]
