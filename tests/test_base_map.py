from ttlru_map._base_map import _BaseMap


def test_base_map__init():
    m: _BaseMap[int, int] = _BaseMap()
    assert m._dict == {}
