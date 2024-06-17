from datetime import timedelta

from ttlru_map import TTLMap


def test_iter():
    d = TTLMap(ttl=timedelta(seconds=1000))
    assert list(d) == []

    d["key1"] = "value"
    assert list(d) == ["key1"]

    d["key2"] = "value"
    assert list(d) == ["key1", "key2"]
