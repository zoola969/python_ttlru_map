from ttlru_map._linked_list import DoubleLinkedListNode


def test_ll_value():
    value = 1
    node: DoubleLinkedListNode[int] = DoubleLinkedListNode(value=value)
    assert node.value == value


def test_ll_equal():
    value = 1
    node1: DoubleLinkedListNode[int] = DoubleLinkedListNode(value=value)
    node2: DoubleLinkedListNode[int] = DoubleLinkedListNode(value=value)
    assert node1 == node2


def test_ll_not_equal():
    value = 1
    node1: DoubleLinkedListNode[int] = DoubleLinkedListNode(value=value)
    node2: DoubleLinkedListNode[int] = DoubleLinkedListNode(value=value + 1)
    assert node1 != node2


def test_ll_not_equal__different_type():
    value = 1
    node: DoubleLinkedListNode[int] = DoubleLinkedListNode(value=value)
    assert node != value
