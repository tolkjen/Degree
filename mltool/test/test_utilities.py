__author__ = 'tolkjen'

from utilities import lists_equiv


def test_lists_equiv():
    assert lists_equiv([1, 2, 3], [3, 2, 1])
    assert lists_equiv([], [])
    assert lists_equiv([[1], [2]], [[2], [1]])
    assert lists_equiv([[1, 2], [3, 4]], [[4, 3], [2, 1]])
    assert not lists_equiv([], [1])
    assert not lists_equiv([1, 1, 2], [1, 2, 2])
