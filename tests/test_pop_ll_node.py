from datetime import timedelta

from ttlru_map import TTLMap


def test_pop_ll_node__middle_node():
    d = TTLMap(ttl=timedelta(seconds=1000))
    head = 1
    middle = 2
    end = 3

    d[head] = 1
    d[middle] = 2
    d[end] = 3

    head_node = d._dict[head].node
    middle_node = d._dict[middle].node
    end_node = d._dict[end].node

    assert head_node.next is middle_node
    assert middle_node.prev is head_node
    assert middle_node.next is end_node
    assert end_node.prev is middle_node
    assert d._ll_head is head_node
    assert d._ll_end is end_node

    d._pop_ll_node(middle_node)

    assert d._ll_head is head_node
    assert d._ll_end is end_node
    assert head_node.next is end_node
    assert end_node.prev is head_node
    assert middle_node.prev is None
    assert middle_node.next is None


def test_pop_ll_node__head_node():
    d = TTLMap(ttl=timedelta(seconds=1000))
    head = 1
    middle = 2
    end = 3

    d[head] = 1
    d[middle] = 2
    d[end] = 3

    head_node = d._dict[head].node
    middle_node = d._dict[middle].node
    end_node = d._dict[end].node

    assert head_node.next is middle_node
    assert middle_node.prev is head_node
    assert middle_node.next is end_node
    assert end_node.prev is middle_node
    assert d._ll_head is head_node
    assert d._ll_end is end_node

    d._pop_ll_node(head_node)

    assert d._ll_head is middle_node
    assert d._ll_end is end_node
    assert middle_node.prev is None
    assert middle_node.next is end_node
    assert head_node.prev is None
    assert head_node.next is None


def test_pop_ll_node__end_node():
    d = TTLMap(ttl=timedelta(seconds=1000))
    head = 1
    middle = 2
    end = 3

    d[head] = 1
    d[middle] = 2
    d[end] = 3

    head_node = d._dict[head].node
    middle_node = d._dict[middle].node
    end_node = d._dict[end].node

    assert head_node.next is middle_node
    assert middle_node.prev is head_node
    assert middle_node.next is end_node
    assert end_node.prev is middle_node
    assert d._ll_head is head_node
    assert d._ll_end is end_node

    d._pop_ll_node(end_node)

    assert d._ll_head is head_node
    assert d._ll_end is middle_node
    assert head_node.next is middle_node
    assert middle_node.prev is head_node
    assert end_node.prev is None
    assert end_node.next is None


def test_pop_ll_node__only_node():
    d = TTLMap(ttl=timedelta(seconds=1000))
    d[1] = 1
    assert d._ll_head is d._ll_end
    d._pop_ll_node(d._ll_head)
    assert d._ll_head is None
    assert d._ll_end is None
