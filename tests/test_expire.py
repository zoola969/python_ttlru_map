import time
from collections import deque
from datetime import timedelta
from unittest.mock import patch

import pytest

from ttl_dict import TTLDict


def test__expiration():
    ttl_dict = TTLDict(ttl=timedelta(days=1), update_ttl_on_get=False)
    key = "test"
    value = "value"
    set_time = time.time()
    check_time = set_time + 1
    access_time = set_time + ttl_dict._ttl.total_seconds() + 1

    with patch("time.time", side_effect=[set_time, check_time, access_time]):
        # Set key
        ttl_dict[key] = value
        # Check key is set
        assert ttl_dict[key] == value

        # Check key is expired next time we try to access it
        with pytest.raises(KeyError):
            ttl_dict[key]

        assert ttl_dict._dict == {}
        assert ttl_dict._deque == deque()
