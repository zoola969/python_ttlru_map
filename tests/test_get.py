import time
from collections import deque
from datetime import timedelta
from unittest.mock import patch

from ttl_dict import TTLDict
from ttl_dict._ttl_dict import _DequeKey, _TTLDictValue


def test__get_item():
    ttl_dict = TTLDict(ttl=timedelta(days=1), update_ttl_on_get=False)
    key = "test"
    value = "value"
    now_time = time.time()

    ttl_dict._dict[key] = _TTLDictValue(value=value, time_=now_time)
    ttl_dict._deque.append(_DequeKey(time_=now_time, key=key))

    with patch("time.time", return_value=now_time):
        assert ttl_dict[key] == value

        assert ttl_dict._dict == {key: _TTLDictValue(value=value, time_=now_time)}
        assert ttl_dict._deque == deque([_DequeKey(time_=now_time, key=key)])


def test__get_item__update_ttl_on_get():
    ttl_dict = TTLDict(ttl=timedelta(days=1), update_ttl_on_get=True)
    key = "test"
    value = "value"
    now_time = time.time()
    next_time = now_time + 100

    with patch("time.time", side_effect=[now_time, next_time]):
        ttl_dict[key] = value

        assert ttl_dict[key] == value
        assert ttl_dict._dict == {key: _TTLDictValue(value=value, time_=next_time)}
        assert ttl_dict._deque == deque([_DequeKey(time_=now_time, key=key), _DequeKey(time_=next_time, key=key)])
