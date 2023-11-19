from collections import deque
from datetime import timedelta
from unittest.mock import Mock, patch

from ttl_dict import TTLDict
from ttl_dict._ttl_dict import _DequeKey, _TTLDictValue

_TIMESTAMP = 946674000.0  # 2000-01-01T00:00:00


@patch("time.time", return_value=_TIMESTAMP)
def test_setitem(time_mock: Mock):
    d = TTLDict(100, timedelta(days=1))
    d["test"] = "value"
    assert d._dict == {"test": _TTLDictValue(value="value", time_=_TIMESTAMP)}
    assert d._deque == deque([_DequeKey(time_=_TIMESTAMP, key="test")])


@patch("time.time", side_effect=[_TIMESTAMP, _TIMESTAMP + 10])
def test_setitem__update(time_mock: Mock):
    d = TTLDict(100, timedelta(days=1))
    d["test"] = "value1"
    d["test"] = "value2"
    assert d._dict == {"test": _TTLDictValue(value="value2", time_=_TIMESTAMP + 10)}
    assert d._deque == deque([_DequeKey(time_=_TIMESTAMP, key="test"), _DequeKey(time_=_TIMESTAMP + 10, key="test")])
