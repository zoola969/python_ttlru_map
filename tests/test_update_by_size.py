from datetime import timedelta

from ttlru_map import TTLMap


def test_update_by_size__unlimited_size():
    ttl = timedelta(seconds=1000)
    d = TTLMap(ttl=ttl, max_size=None)
    size = 1000
    for i in range(size):
        d[i] = i
    d._update_by_size()
    assert len(d) == size


def test_update_by_size__empty_dict():
    ttl = timedelta(seconds=1000)
    d = TTLMap(ttl=ttl, max_size=100)
    d._update_by_size()
    assert len(d) == 0


def test_update_by_size__dict_full():
    ttl = timedelta(seconds=1000)
    size = 3
    d = TTLMap(ttl=ttl, max_size=size)
    for i in range(size):
        d[i] = i
    assert len(d) == size
    d._max_size -= 1
    d._update_by_size()
    assert len(d) == size - 1
    assert d._dict == {i: d._dict[i] for i in range(1, size)}
    assert d._ll_head == d._dict[1].node
    assert d._ll_end == d._dict[size - 1].node


def test_update_by_size__rm_last_item():
    ttl = timedelta(seconds=1000)
    d = TTLMap(ttl=ttl, max_size=1)
    d[1] = 1
    assert len(d) == 1
    d._max_size = 0
    d._update_by_size()
    assert len(d) == 0
    assert d._ll_head is None
    assert d._ll_end is None
