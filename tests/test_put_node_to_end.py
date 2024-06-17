from datetime import timedelta

from ttlru_map import TTLMap
from ttlru_map._linked_list import DoubleLinkedListNode
from ttlru_map._ttl_map import _LinkedListValue


def test_put_node_to_end__empty_dict():
    d = TTLMap(ttl=timedelta(seconds=100))
    assert d._ll_head is None
    assert d._ll_end is None
    node = DoubleLinkedListNode(value=_LinkedListValue(time_=1, key=1))
    d._put_node_to_end(node=node)

    assert d._ll_head is node
    assert d._ll_end is node
    assert node.next is None
    assert node.prev is None


def test_put_node_to_end__not_empty_dict():
    d = TTLMap(ttl=timedelta(seconds=100))

    d[1] = 1
    d[2] = 2

    head_node = d._ll_head
    end_node = d._ll_end
    assert head_node is not None
    assert end_node is not None
    assert head_node is d._dict[1].node
    assert end_node is d._dict[2].node

    node = DoubleLinkedListNode(value=_LinkedListValue(time_=1, key=3))
    d._put_node_to_end(node=node)

    assert d._ll_head is head_node
    assert d._ll_end is node

    assert head_node.next is end_node
    assert end_node.prev is head_node
    assert end_node.next is node
    assert node.prev is end_node
    assert node.next is None
