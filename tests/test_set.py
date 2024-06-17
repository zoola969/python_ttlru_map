from datetime import timedelta
from unittest.mock import patch

from tests.utils import LockMock
from ttlru_map import TTLMap
from ttlru_map._linked_list import DoubleLinkedListNode
from ttlru_map._ttl_map import _DictValue, _LinkedListValue


def test_set__first():
    d = TTLMap(ttl=timedelta(seconds=1000))
    lock_mock = LockMock()
    d._lock = lock_mock
    key = 1
    value = 2
    time_ = 10
    expected_node = DoubleLinkedListNode(value=_LinkedListValue(time_=time_, key=key))
    with patch("time.time", return_value=time_) as time_mock, patch.object(
        TTLMap,
        "_setitem",
        wraps=d._setitem,
    ) as setitem_mock, patch.object(
        TTLMap,
        "_update_by_ttl",
        wraps=d._update_by_ttl,
    ) as update_by_ttl_mock, patch.object(
        TTLMap,
        "_update_by_size",
        wraps=d._update_by_size,
    ) as update_by_size_mock:
        d[key] = value
        time_mock.assert_called_once()
        setitem_mock.assert_called_once_with(key, value, time_)
        update_by_ttl_mock.assert_called_once_with(current_time=time_)
        update_by_size_mock.assert_called_once()
        lock_mock.__enter__.assert_called_once()
        lock_mock.__exit__.assert_called_once()
        assert d[key] == value
        assert d._dict == {key: _DictValue(value=value, node=expected_node)}
        assert d._ll_head == expected_node
        assert d._ll_end == expected_node


def test_set__second():
    d = TTLMap(ttl=timedelta(seconds=1000))
    head_key = 1
    head_value = 2
    d[head_key] = head_value
    head_item = d._dict[head_key]
    lock_mock = LockMock()
    d._lock = lock_mock
    new_key = 5
    new_value = 20
    time_ = 10
    expected_node = DoubleLinkedListNode(value=_LinkedListValue(time_=time_, key=new_key))
    with patch("time.time", return_value=time_) as time_mock, patch.object(
        TTLMap,
        "_setitem",
        wraps=d._setitem,
    ) as setitem_mock, patch.object(
        TTLMap,
        "_update_by_ttl",
        wraps=d._update_by_ttl,
    ) as update_by_ttl_mock, patch.object(
        TTLMap,
        "_update_by_size",
        wraps=d._update_by_size,
    ) as update_by_size_mock:
        d[new_key] = new_value
        time_mock.assert_called_once()
        setitem_mock.assert_called_once_with(new_key, new_value, time_)
        update_by_ttl_mock.assert_called_once_with(current_time=time_)
        update_by_size_mock.assert_called_once()
        lock_mock.__enter__.assert_called_once()
        lock_mock.__exit__.assert_called_once()
        assert d[new_key] == new_value
        end_node = d._dict[new_key].node
        assert expected_node == end_node
        assert d._dict == {
            head_key: head_item,
            new_key: _DictValue(value=new_value, node=end_node),
        }
        assert d._ll_head is head_item.node
        assert d._ll_end is end_node
        assert head_item.node.next == end_node
        assert end_node.prev == head_item.node
