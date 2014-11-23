__author__ = 'tolkjen'

import pytest

from ..spaces import RemoveSpace, NormalizeSpace, SpaceException, FixSpace, ClassificationSpace, QuantifySpace, \
    SearchSpace
from ..descriptors import PreprocessingDescriptor


def validate_space_default_constructor(space_type):
    space = space_type()
    descriptor = PreprocessingDescriptor()
    data = [1 for _ in space.generate(descriptor)]
    assert len(data) > 0


def test_fix_space_default_constructor():
    validate_space_default_constructor(FixSpace)


def test_remove_space_default_constructor():
    validate_space_default_constructor(RemoveSpace)


def test_normalize_space_default_constructor():
    validate_space_default_constructor(NormalizeSpace)


def test_quantify_space_default_constructor():
    validate_space_default_constructor(QuantifySpace)


def test_remove_space_missing_arguments():
    space0 = RemoveSpace([], [])
    descriptors0 = [x for x in space0.generate(PreprocessingDescriptor())]
    assert len(descriptors0) == 1
    assert descriptors0[0].removed_columns == []

    space1 = RemoveSpace([], [0])
    descriptors1 = [x for x in space1.generate(PreprocessingDescriptor())]
    assert len(descriptors1) == 1
    assert descriptors1[0].removed_columns == []

    with pytest.raises(SpaceException):
        RemoveSpace([1], [])

    with pytest.raises(SpaceException):
        RemoveSpace([], [1])


def test_normalize_space_missing_arguments():
    space0 = NormalizeSpace([], [])
    descriptors0 = [x for x in space0.generate(PreprocessingDescriptor())]
    assert len(descriptors0) == 1
    assert descriptors0[0].normalized_columns == []

    space1 = NormalizeSpace([], [0])
    descriptors1 = [x for x in space1.generate(PreprocessingDescriptor())]
    assert len(descriptors1) == 1
    assert descriptors1[0].normalized_columns == []

    with pytest.raises(SpaceException):
        NormalizeSpace([1], [])

    with pytest.raises(SpaceException):
        NormalizeSpace([], [1])


def test_quantify_space():
    columns = ["a", "b", "c", "d"]
    algorithms = ["k-means"]
    group_sizes = [1]
    max_columns = 4
    granularity = 2

    space = QuantifySpace(columns, algorithms, group_sizes, max_columns, granularity)
    count = sum((1 for _ in space.generate(PreprocessingDescriptor())))
    assert count == (4 + 6 + 4 + 1) * granularity


def test_quantify_space_2():
    columns = ["a", "b", "c", "d"]
    algorithms = ["k-means"]
    group_sizes = [2]
    max_columns = 4
    granularity = 2

    space = QuantifySpace(columns, algorithms, group_sizes, max_columns, granularity)
    count = sum((1 for _ in space.generate(PreprocessingDescriptor())))
    assert count == (6 + 12 + 3 + 4) * granularity * granularity


def test_search_space_with_removed_cols():
    columns = ["a", "b", "c", "d"]
    granularity = 2

    fix_space = FixSpace(["remove"])
    remove_space = RemoveSpace(columns, [1])
    normalize_space = NormalizeSpace(columns, [len(columns)])
    quantify_space = QuantifySpace(columns, [], [0], 3, granularity)
    classify_space = ClassificationSpace(["tree"], granularity)

    search_space = SearchSpace(fix_space, remove_space, normalize_space, quantify_space, classify_space)

    descriptors = [x for x in search_space]
    assert len(descriptors) == 0
