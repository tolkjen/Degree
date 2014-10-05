__author__ = 'tolkjen'

import pytest

from ..generators import SubsetGenerator, GeneratorException
from utilities import lists_equiv


def test_subset_generator_size_too_big():
    with pytest.raises(GeneratorException):
        SubsetGenerator([0, 1, 2], 10)


def test_subset_generator_size_zero():
    generator = SubsetGenerator([1, 2, 3], 0)
    items = [x for x in generator]
    assert items == []


def test_subset_generator_size_zero_no_objects():
    generator = SubsetGenerator([], 0)
    items = [x for x in generator]
    assert items == []


def test_subset_generator():
    g1 = SubsetGenerator([1, 2, 3], 1)
    assert lists_equiv([x for x in g1], [[1], [2], [3]])

    g2 = SubsetGenerator([1, 2, 3], 2)
    assert lists_equiv([x for x in g2], [[1, 2], [2, 3], [3, 1]])

    g3 = SubsetGenerator([1, 2, 3], 3)
    assert lists_equiv([x for x in g3], [[1, 2, 3]])
