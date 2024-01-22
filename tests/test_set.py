import time
from collections import deque
from datetime import timedelta
from unittest.mock import patch

import pytest

from ttl_dict import TTLDict
from ttl_dict._ttl_dict import _DequeKey, _TTLDictValue


def test__set_item():
    ttl_dict = TTLDict(ttl=timedelta(days=1), update_ttl_on_get=False)
    key = "test"
    value = "value"
    now_time = time.time()

    with patch("time.time", return_value=now_time):
        ttl_dict[key] = value

        assert ttl_dict[key] == value
        assert ttl_dict._dict == {key: _TTLDictValue(value=value, time_=now_time)}
        assert ttl_dict._deque == deque([_DequeKey(time_=now_time, key=key)])


def test__set_item__exceed_max_size():
    ttl_dict = TTLDict(max_size=1, ttl=timedelta(days=1), update_ttl_on_get=False)
    key1 = "test1"
    value1 = "value1"
    key2 = "test2"
    value2 = "value2"
    first_set_time = time.time()
    second_set_time = first_set_time + 1
    access_time = second_set_time + 1

    with patch("time.time", side_effect=[first_set_time, second_set_time, access_time, access_time]):
        ttl_dict[key1] = value1
        ttl_dict[key2] = value2

        assert ttl_dict[key2] == value2
        with pytest.raises(KeyError):
            ttl_dict[key1]
        assert ttl_dict._dict == {key2: _TTLDictValue(value=value2, time_=second_set_time)}
        assert ttl_dict._deque == deque([_DequeKey(time_=second_set_time, key=key2)])


def test__set_item__update_full_dict():
    ttl_dict = TTLDict(max_size=2, ttl=timedelta(days=1), update_ttl_on_get=False)
    key1 = "test1"
    value1 = "value1"
    key2 = "test2"
    value2 = "value2"
    value3 = "value3"

    first_set_time = time.time()
    second_set_time = first_set_time + 1
    check_time = second_set_time + 1
    update_time = check_time + 1
    second_check_time = update_time + 1

    with patch(
        "time.time",
        side_effect=[first_set_time, second_set_time, check_time, update_time, second_check_time],
    ):
        # Set two items to dict
        # Now dict is full and if we try to overflow it, the oldest item will be removed (key1, value1)
        ttl_dict[key1] = value1
        ttl_dict[key2] = value2
        # Check that items are in dict
        assert len(ttl_dict) == 2
        # Update value of the newest item (key2, value2)
        ttl_dict[key2] = value3
        # Check that no items were removed from dict
        assert len(ttl_dict) == 2
        assert ttl_dict._dict == {
            key1: _TTLDictValue(value=value1, time_=first_set_time),
            key2: _TTLDictValue(value=value3, time_=update_time),
        }
        assert ttl_dict._deque == deque(
            [
                _DequeKey(time_=first_set_time, key=key1),
                _DequeKey(time_=second_set_time, key=key2),
                _DequeKey(time_=update_time, key=key2),
            ],
        )
