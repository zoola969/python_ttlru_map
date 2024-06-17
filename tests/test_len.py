from datetime import timedelta

from ttlru_map import TTLMap


def test_len():
    d = TTLMap(ttl=timedelta(seconds=1000))
    assert len(d) == 0

    d[1] = 1
    assert len(d) == 1

    d[2] = 2
    assert len(d) == 2

    d[3] = 3
    assert len(d) == 3

    del d[1]
    assert len(d) == 2

    del d[2]
    assert len(d) == 1

    del d[3]
    assert len(d) == 0
