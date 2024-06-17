import time
from datetime import timedelta
from unittest.mock import patch

from ttlru_map import TTLMap
from ttlru_map._linked_list import DoubleLinkedListNode
from ttlru_map._ttl_map import _DictValue, _LinkedListValue


def test_update_by_ttl__empty_dict():
    d = TTLMap(ttl=timedelta(seconds=1000))
    d._update_by_ttl()


def test_update_by_ttl__last_item():
    ttl = timedelta(seconds=100)
    d = TTLMap(ttl=ttl)
    time_ = time.time() + ttl.total_seconds() + 1
    d._update_by_ttl(current_time=time_)
    assert d._ll_head is None
    assert d._ll_end is None
    assert d._dict == {}


def test_update_by_ttl__expired_head():
    ttl = timedelta(seconds=100)
    d = TTLMap(ttl=ttl)
    k1 = 1
    k2 = 2
    v1 = 1
    v2 = 2
    set_time_1 = 1
    set_time_2 = set_time_1 + ttl.total_seconds() + 1
    with patch("time.time", side_effect=[set_time_1, set_time_2]):
        d[k1] = v1
        d[k2] = v2
    d._update_by_ttl(current_time=set_time_2)
    node_2 = DoubleLinkedListNode(value=_LinkedListValue(time_=set_time_2, key=k2))
    assert d._ll_head == node_2
    assert d._ll_end == node_2
    assert d._dict == {k2: _DictValue(node=node_2, value=v2)}


def test_update_by_ttl__unlimited_ttl():
    size = 1000
    d = TTLMap(ttl=None, max_size=size)
    for i in range(size):
        d[i] = i
    d._update_by_ttl()
    assert len(d) == size
