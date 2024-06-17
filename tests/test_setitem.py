from datetime import timedelta
from unittest.mock import patch

from ttlru_map import TTLMap
from ttlru_map._linked_list import DoubleLinkedListNode
from ttlru_map._ttl_map import _DictValue, _LinkedListValue


def test_setitem__new_item():
    d = TTLMap(ttl=timedelta(seconds=1000))
    time_ = 100.0
    key = 1
    value = 1
    expected_node = DoubleLinkedListNode(value=_LinkedListValue(time_=time_, key=key))
    with patch.object(TTLMap, "_pop_ll_node") as mock_pop_ll_node, patch.object(
        TTLMap,
        "_put_node_to_end",
    ) as mock_put_node_to_end:
        d._setitem(key, value, time_)
        mock_pop_ll_node.assert_not_called()
        mock_put_node_to_end.assert_called_once()
        assert mock_put_node_to_end.call_args[0][0] == expected_node
    assert d._dict == {key: _DictValue(value=value, node=expected_node)}


def test_setitem__existing_item():
    d = TTLMap(ttl=timedelta(seconds=1000))
    time_ = 100.0
    key = 1
    value = 1
    d[key] = value
    old_node = d._dict[key].node
    expected_node = DoubleLinkedListNode(value=_LinkedListValue(time_=time_, key=key))
    with patch.object(TTLMap, "_pop_ll_node") as mock_pop_ll_node, patch.object(
        TTLMap,
        "_put_node_to_end",
    ) as mock_put_node_to_end:
        d._setitem(key, value, time_)
        mock_pop_ll_node.assert_called_once_with(old_node)
        mock_put_node_to_end.assert_called_once()
        assert mock_put_node_to_end.call_args[0][0] == expected_node
    assert d._dict == {key: _DictValue(value=value, node=expected_node)}
