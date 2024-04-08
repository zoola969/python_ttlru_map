from datetime import timedelta

import pytest

from ttl_dict import TTLDict, TTLDictInvalidConfigError


@pytest.mark.parametrize(
    ("ttl", "max_size", "update_ttl_on_get"),
    [
        (timedelta(seconds=1), 1, True),
        (timedelta(seconds=1), 1, False),
        (timedelta(seconds=1), None, True),
        (None, 1, False),
    ],
)
def test_init__ok(ttl: timedelta | None, max_size: int | None, update_ttl_on_get: bool):
    TTLDict(ttl=ttl, max_size=max_size, update_ttl_on_get=update_ttl_on_get)


@pytest.mark.parametrize(
    ("ttl", "max_size", "update_ttl_on_get"),
    [
        (None, None, False),
        (None, None, True),
        (timedelta(seconds=0), 1, True),
        (timedelta(seconds=-1), 1, True),
        (timedelta(seconds=1), 0, False),
        (timedelta(seconds=1), -1, True),
        (None, 1, True),
    ],
)
def test_init_error(ttl: timedelta | None, max_size: int | None, update_ttl_on_get: bool):
    with pytest.raises(TTLDictInvalidConfigError):
        TTLDict(ttl=ttl, max_size=max_size, update_ttl_on_get=update_ttl_on_get)
