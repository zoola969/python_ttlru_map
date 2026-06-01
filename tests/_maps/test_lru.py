from __future__ import annotations

import threading
from contextlib import suppress
from typing import TYPE_CHECKING

import pytest

from tests.utils import LockMock
from ttlru_map import TTLMapInvalidConfigError
from ttlru_map._linked_list import DoubleLinkedListNode
from ttlru_map._maps._lru import LruMap

if TYPE_CHECKING:
    from collections.abc import Callable

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _ll_keys(d: LruMap[int, int]) -> list[int]:
    """Walk the doubly-linked list head -> tail and return the key order."""
    keys: list[int] = []
    node = d._ll_head
    seen: set[int] = set()
    while node is not None:
        assert id(node) not in seen, "cycle in linked list"
        seen.add(id(node))
        keys.append(node.value)
        node = node.next
    return keys


def _ll_keys_reverse(d: LruMap[int, int]) -> list[int]:
    """Walk the doubly-linked list tail -> head and return the key order."""
    keys: list[int] = []
    node = d._ll_tail
    seen: set[int] = set()
    while node is not None:
        assert id(node) not in seen, "cycle in linked list"
        seen.add(id(node))
        keys.append(node.value)
        node = node.prev
    return keys


def _assert_ll_consistent(d: LruMap[int, int]) -> None:
    """Assert LL consistency.

    Both walks must agree, head.prev/tail.next must be None, and the LL
    key set must equal the dict key set.
    """
    fwd = _ll_keys(d)
    rev = _ll_keys_reverse(d)
    assert fwd == list(reversed(rev))
    assert set(fwd) == set(d._dict)
    if d._dict:
        assert d._ll_head is not None
        assert d._ll_tail is not None
        assert d._ll_head.prev is None
        assert d._ll_tail.next is None
    else:
        assert d._ll_head is None
        assert d._ll_tail is None


def _run_threads(targets: list[threading.Thread]) -> None:
    for t in targets:
        t.start()
    for t in targets:
        t.join()


# --------------------------------------------------------------------------- #
# __init__
# --------------------------------------------------------------------------- #


def test_init() -> None:
    d: LruMap[int, int] = LruMap(max_size=10)
    assert d._dict == {}
    assert d._ll_head is None
    assert d._ll_tail is None
    assert d._max_size == 10


@pytest.mark.parametrize("bad", [0, -1, None, 1.5, True, "10"])
def test_init__rejects_invalid_max_size(bad: object) -> None:
    with pytest.raises(TTLMapInvalidConfigError):
        LruMap(max_size=bad)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# _put_node_to_end
# --------------------------------------------------------------------------- #


def test_put_node_to_end__empty() -> None:
    d: LruMap[int, int] = LruMap(max_size=10)
    node = DoubleLinkedListNode(value=1)
    d._put_node_to_end(node)
    assert d._ll_head is node
    assert d._ll_tail is node
    assert node.prev is None
    assert node.next is None


def test_put_node_to_end__non_empty() -> None:
    d: LruMap[int, int] = LruMap(max_size=10)
    d[1] = 1
    d[2] = 2
    head_node = d._ll_head
    tail_node = d._ll_tail

    node = DoubleLinkedListNode(value=3)
    d._put_node_to_end(node)

    assert d._ll_head is head_node
    assert d._ll_tail is node
    assert tail_node.next is node
    assert node.prev is tail_node
    assert node.next is None


# --------------------------------------------------------------------------- #
# _pop_ll_node
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("setup_keys", "pop_idx", "expected_ll"),
    [
        pytest.param([1, 2, 3], 1, [1, 3], id="middle"),
        pytest.param([1, 2, 3], 0, [2, 3], id="head"),
        pytest.param([1, 2, 3], 2, [1, 2], id="tail"),
        pytest.param([1], 0, [], id="only"),
    ],
)
def test_pop_ll_node(setup_keys: list[int], pop_idx: int, expected_ll: list[int]) -> None:
    d: LruMap[int, int] = LruMap(max_size=10)
    for k in setup_keys:
        d[k] = k
    target = d._dict[setup_keys[pop_idx]].node

    d._pop_ll_node(target)

    assert _ll_keys(d) == expected_ll
    assert _ll_keys_reverse(d) == list(reversed(expected_ll))
    assert target.prev is None
    assert target.next is None
    if expected_ll:
        assert d._ll_head is d._dict[expected_ll[0]].node
        assert d._ll_tail is d._dict[expected_ll[-1]].node
    else:
        assert d._ll_head is None
        assert d._ll_tail is None


# --------------------------------------------------------------------------- #
# _setitem
# --------------------------------------------------------------------------- #


def test_setitem__new_item() -> None:
    d: LruMap[int, int] = LruMap(max_size=10)
    d._setitem(1, 2)
    assert d._dict[1].value == 2
    assert d._dict[1].node is d._ll_tail
    assert d._ll_head is d._ll_tail
    _assert_ll_consistent(d)


def test_setitem__existing_item_updates_value_and_moves_to_tail() -> None:
    d: LruMap[int, int] = LruMap(max_size=10)
    d[1] = 1
    d[2] = 2
    old_node = d._dict[1].node

    d._setitem(1, 11)

    assert d._dict[1].value == 11
    assert d._dict[1].node is not old_node
    assert d._ll_tail is d._dict[1].node
    assert old_node.prev is None
    assert old_node.next is None
    _assert_ll_consistent(d)


# --------------------------------------------------------------------------- #
# _delitem
# --------------------------------------------------------------------------- #


def test_delitem_internal() -> None:
    d: LruMap[int, int] = LruMap(max_size=10)
    d[1] = 1
    item = d._dict[1]
    d._delitem(item)
    assert d._dict == {}
    _assert_ll_consistent(d)


# --------------------------------------------------------------------------- #
# _update_by_size
# --------------------------------------------------------------------------- #


def test_update_by_size__empty() -> None:
    d: LruMap[int, int] = LruMap(max_size=10)
    d._update_by_size()
    assert d._dict == {}
    _assert_ll_consistent(d)


def test_update_by_size__under_limit() -> None:
    d: LruMap[int, int] = LruMap(max_size=10)
    for i in range(5):
        d[i] = i
    d._update_by_size()
    assert len(d._dict) == 5


def test_update_by_size__over_limit() -> None:
    size = 3
    d: LruMap[int, int] = LruMap(max_size=size)
    for i in range(size):
        d[i] = i
    d._max_size -= 1
    d._update_by_size()
    assert len(d._dict) == size - 1
    assert 0 not in d._dict
    assert d._ll_head is d._dict[1].node
    assert d._ll_tail is d._dict[size - 1].node


def test_update_by_size__rm_all() -> None:
    d: LruMap[int, int] = LruMap(max_size=1)
    d[1] = 1
    d._max_size = 0
    d._update_by_size()
    assert d._dict == {}
    _assert_ll_consistent(d)


# --------------------------------------------------------------------------- #
# public mutators take the lock
# --------------------------------------------------------------------------- #


def test_setitem_public__takes_lock() -> None:
    d: LruMap[int, int] = LruMap(max_size=10)
    lock_mock = LockMock()
    d._lock = lock_mock
    d[1] = 2
    assert d._dict[1].value == 2
    lock_mock.__enter__.assert_called_once()
    lock_mock.__exit__.assert_called_once()


def test_getitem_public__takes_lock() -> None:
    d: LruMap[int, int] = LruMap(max_size=10)
    d[1] = 1
    lock_mock = LockMock()
    d._lock = lock_mock
    assert d[1] == 1
    lock_mock.__enter__.assert_called_once()
    lock_mock.__exit__.assert_called_once()


def test_delitem_public__takes_lock() -> None:
    d: LruMap[int, int] = LruMap(max_size=10)
    d[1] = 1
    lock_mock = LockMock()
    d._lock = lock_mock
    del d[1]
    assert 1 not in d._dict
    lock_mock.__enter__.assert_called_once()
    lock_mock.__exit__.assert_called_once()


# --------------------------------------------------------------------------- #
# Missing-key behavior
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "op",
    [
        pytest.param(lambda d: d[99], id="getitem"),
        pytest.param(lambda d: d.__delitem__(99), id="delitem"),
        pytest.param(lambda d: d.pop(99), id="pop_no_default"),
        pytest.param(lambda d: d.popitem(), id="popitem_empty"),
    ],
)
def test_missing_key_raises(op: Callable[[LruMap[int, int]], object]) -> None:
    d: LruMap[int, int] = LruMap(max_size=3)
    with pytest.raises(KeyError):
        op(d)


# --------------------------------------------------------------------------- #
# __len__ / __iter__
# --------------------------------------------------------------------------- #


def test_len() -> None:
    d: LruMap[int, int] = LruMap(max_size=10)
    assert len(d) == 0
    d[1] = 1
    d[2] = 2
    assert len(d) == 2
    del d[1]
    assert len(d) == 1


def test_iter__preserves_insertion_order() -> None:
    d: LruMap[int, int] = LruMap(max_size=10)
    assert list(d) == []
    d[1] = 1
    d[2] = 2
    d[3] = 3
    assert list(d) == [1, 2, 3]


def test_iter__unchanged_by_get_promotion() -> None:
    """``list(d)`` follows dict insertion order even after a promoting get.

    LL order diverges from iteration order — this is intentional.
    """
    d: LruMap[int, int] = LruMap(max_size=3)
    d[1] = 1
    d[2] = 2
    d[3] = 3
    _ = d[1]  # promote 1 in the LL only
    assert list(d) == [1, 2, 3]
    assert _ll_keys(d) == [2, 3, 1]


# --------------------------------------------------------------------------- #
# LRU strategy end-to-end
# --------------------------------------------------------------------------- #


def test_lru__get_promotes_to_most_recent() -> None:
    d: LruMap[int, int] = LruMap(max_size=3)
    d[1] = 1
    d[2] = 2
    d[3] = 3

    _ = d[1]  # promote 1

    assert _ll_keys(d) == [2, 3, 1]
    _assert_ll_consistent(d)

    d[4] = 4  # should evict 2 (now oldest)

    assert 2 not in d._dict
    assert _ll_keys(d) == [3, 1, 4]
    _assert_ll_consistent(d)


def test_lru__set_existing_promotes_to_most_recent() -> None:
    d: LruMap[int, int] = LruMap(max_size=3)
    d[1] = 1
    d[2] = 2
    d[3] = 3

    d[2] = 22  # update existing -> promote

    assert _ll_keys(d) == [1, 3, 2]
    assert d._dict[2].value == 22
    _assert_ll_consistent(d)

    d[4] = 4  # evicts 1

    assert 1 not in d._dict
    assert _ll_keys(d) == [3, 2, 4]
    _assert_ll_consistent(d)


def test_lru__pure_insertion_evicts_in_order() -> None:
    d: LruMap[int, int] = LruMap(max_size=3)
    for i in range(6):
        d[i] = i
    assert _ll_keys(d) == [3, 4, 5]
    assert set(d._dict) == {3, 4, 5}
    _assert_ll_consistent(d)


def test_lru__update_at_max_size_does_not_evict() -> None:
    """Updating an existing key when at max_size keeps len constant — nothing is evicted."""
    d: LruMap[int, int] = LruMap(max_size=3)
    d[1] = 1
    d[2] = 2
    d[3] = 3

    d[1] = 11

    assert set(d._dict) == {1, 2, 3}
    assert d._dict[1].value == 11
    assert _ll_keys(d) == [2, 3, 1]
    _assert_ll_consistent(d)


def test_lru__delitem_head() -> None:
    """Deleting the head advances head to the next node."""
    d: LruMap[int, int] = LruMap(max_size=10)
    d[1] = 1
    d[2] = 2
    d[3] = 3
    del d[1]
    assert _ll_keys(d) == [2, 3]
    assert d._ll_head is d._dict[2].node
    _assert_ll_consistent(d)


def test_lru__delitem_tail() -> None:
    """Deleting the tail rewinds tail to the previous node."""
    d: LruMap[int, int] = LruMap(max_size=10)
    d[1] = 1
    d[2] = 2
    d[3] = 3
    del d[3]
    assert _ll_keys(d) == [1, 2]
    assert d._ll_tail is d._dict[2].node
    _assert_ll_consistent(d)


# --------------------------------------------------------------------------- #
# Concurrent access
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("max_size", "n_threads", "per_thread"),
    [
        pytest.param(1600, 16, 100, id="under_max_size"),
        pytest.param(50, 16, 200, id="over_max_size"),
    ],
)
def test_concurrent_setitem(max_size: int, n_threads: int, per_thread: int) -> None:
    """Many threads insert distinct keys; final state is bounded and LL stays consistent.

    When max_size >= total, every inserted key must survive.
    """
    total = n_threads * per_thread
    d: LruMap[int, int] = LruMap(max_size=max_size)

    def worker(start: int) -> None:
        for i in range(start, start + per_thread):
            d[i] = i

    _run_threads(
        [threading.Thread(target=worker, args=(t * per_thread,)) for t in range(n_threads)],
    )

    expected_len = min(total, max_size)
    assert len(d) == expected_len
    if max_size >= total:
        assert set(d._dict) == set(range(total))
    _assert_ll_consistent(d)


def _mixed_setter(d: LruMap[int, int], iterations: int, max_size: int, errors: list[BaseException]) -> None:
    try:
        for i in range(iterations):
            d[i % (max_size * 4)] = i
    except BaseException as e:  # noqa: BLE001
        errors.append(e)


def _mixed_getter(d: LruMap[int, int], iterations: int, max_size: int, errors: list[BaseException]) -> None:
    try:
        for i in range(iterations):
            with suppress(KeyError):
                _ = d[i % max_size]
    except BaseException as e:  # noqa: BLE001
        errors.append(e)


def _mixed_deleter(d: LruMap[int, int], iterations: int, max_size: int, errors: list[BaseException]) -> None:
    try:
        for i in range(iterations):
            with suppress(KeyError):
                del d[i % max_size]
    except BaseException as e:  # noqa: BLE001
        errors.append(e)


def test_concurrent_mixed_ops__no_corruption() -> None:
    """Concurrent setitem / getitem / delitem must not raise and must leave dict/LL consistent."""
    max_size = 64
    iterations = 2000
    d: LruMap[int, int] = LruMap(max_size=max_size)
    # Pre-seed so getters/deleters have something to find.
    for i in range(max_size):
        d[i] = i

    errors: list[BaseException] = []
    args = (d, iterations, max_size, errors)

    _run_threads(
        [threading.Thread(target=_mixed_setter, args=args) for _ in range(4)]
        + [threading.Thread(target=_mixed_getter, args=args) for _ in range(4)]
        + [threading.Thread(target=_mixed_deleter, args=args) for _ in range(2)],
    )

    assert errors == []
    _assert_ll_consistent(d)


# --------------------------------------------------------------------------- #
# Read paths must not promote
# --------------------------------------------------------------------------- #


def test_contains__does_not_promote() -> None:
    d: LruMap[int, int] = LruMap(max_size=3)
    d[1] = 1
    d[2] = 2
    d[3] = 3
    lock_mock = LockMock()
    d._lock = lock_mock

    assert (1 in d) is True
    assert (99 in d) is False

    assert _ll_keys(d) == [1, 2, 3]
    # __contains__ takes the lock once per call.
    assert lock_mock.__enter__.call_count == 2
    assert lock_mock.__exit__.call_count == 2


def test_get__does_not_promote_and_returns_default() -> None:
    d: LruMap[int, int] = LruMap(max_size=3)
    d[1] = 1
    d[2] = 2
    d[3] = 3
    lock_mock = LockMock()
    d._lock = lock_mock

    assert d.get(1) == 1
    assert d.get(2) == 2
    assert d.get(99) is None
    assert d.get(99, "fallback") == "fallback"

    assert _ll_keys(d) == [1, 2, 3]
    assert lock_mock.__enter__.call_count == 4


# --------------------------------------------------------------------------- #
# Atomic pop / popitem
# --------------------------------------------------------------------------- #


def test_pop__removes_under_single_lock() -> None:
    d: LruMap[int, int] = LruMap(max_size=3)
    d[1] = 1
    d[2] = 2
    d[3] = 3
    lock_mock = LockMock()
    d._lock = lock_mock

    assert d.pop(2) == 2

    assert 2 not in d._dict
    assert _ll_keys(d) == [1, 3]
    # Single critical section, no getitem/delitem two-step.
    assert lock_mock.__enter__.call_count == 1
    assert lock_mock.__exit__.call_count == 1


@pytest.mark.parametrize(
    ("default", "expected"),
    [
        pytest.param("fallback", "fallback", id="string"),
        pytest.param(None, None, id="none"),
    ],
)
def test_pop__missing_returns_default(default: object, expected: object) -> None:
    d: LruMap[int, int] = LruMap(max_size=3)
    d[1] = 1
    assert d.pop(99, default) == expected


def test_popitem__evicts_lru_head() -> None:
    d: LruMap[int, int] = LruMap(max_size=3)
    d[1] = 1
    d[2] = 2
    d[3] = 3
    _ = d[1]  # LL: [2, 3, 1] — head is 2

    key, value = d.popitem()
    assert (key, value) == (2, 2)
    assert _ll_keys(d) == [3, 1]
    _assert_ll_consistent(d)


def test_popitem__leaves_empty_state() -> None:
    """Popping the last item resets head/tail to None."""
    d: LruMap[int, int] = LruMap(max_size=3)
    d[1] = 1
    key, value = d.popitem()
    assert (key, value) == (1, 1)
    assert d._dict == {}
    _assert_ll_consistent(d)
