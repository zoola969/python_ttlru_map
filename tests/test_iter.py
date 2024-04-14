from datetime import timedelta

from ttl_dict import TTLDict


def test_iter():
    d = TTLDict(ttl=timedelta(seconds=1000))
    assert list(d) == []

    d["key1"] = "value"
    assert list(d) == ["key1"]

    d["key2"] = "value"
    assert list(d) == ["key1", "key2"]
