from ttl_dict._linked_list import DoubleLinkedListNode


def test_ll_value():
    value = 1
    l: DoubleLinkedListNode[int] = DoubleLinkedListNode(value=value)
    assert l.value == value


def test_ll_equal():
    value = 1
    l1: DoubleLinkedListNode[int] = DoubleLinkedListNode(value=value)
    l2: DoubleLinkedListNode[int] = DoubleLinkedListNode(value=value)
    assert l1 == l2


def test_ll_not_equal():
    value = 1
    l1: DoubleLinkedListNode[int] = DoubleLinkedListNode(value=value)
    l2: DoubleLinkedListNode[int] = DoubleLinkedListNode(value=value + 1)
    assert l1 != l2


def test_ll_not_equal__different_type():
    value = 1
    l1: DoubleLinkedListNode[int] = DoubleLinkedListNode(value=value)
    assert l1 != value
