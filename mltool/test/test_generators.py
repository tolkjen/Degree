__author__ = 'tolkjen'

import pytest

from ..generators import SubsetGenerator, GeneratorException, MultiSubsetGenerator, ParameterCombinationGenerator
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


def test_parameter_subset_generator():
    params_one = [1]
    params_two = ["a"]

    generator = ParameterCombinationGenerator([params_one, params_two])
    combinations = [x for x in generator]

    assert len(combinations) == 1
    assert combinations[0] == [1, "a"]


def test_parameter_subset_generator_2():
    params_one = [1, 2, 3]
    params_two = ["a", "b"]

    generator = ParameterCombinationGenerator([params_one, params_two])
    combinations = [x for x in generator]

    assert len(combinations) == 6
    assert combinations[0] == [1, "a"]
    assert combinations[1] == [1, "b"]
    assert combinations[2] == [2, "a"]
    assert combinations[3] == [2, "b"]
    assert combinations[4] == [3, "a"]
    assert combinations[5] == [3, "b"]


def test_multi_subset_generator():
    columns = ["a", "b", "c", "d"]
    objects = ["cat", "cat"]
    distribution = [2, 2]

    generator = MultiSubsetGenerator(columns, objects, distribution)
    count = sum((1 for _ in generator))

    assert count == 3
    for subsets in generator:
        assert not lists_equiv(subsets[0], subsets[1])

def test_multi_subset_generator_2():
    columns = ["a", "b", "c", "d"]
    objects = ["cat", "cat"]
    distribution = [1, 2]

    generator = MultiSubsetGenerator(columns, objects, distribution)
    count = sum((1 for _ in generator))

    assert count == 12
    for subsets in generator:
        assert not lists_equiv(subsets[0], subsets[1])
