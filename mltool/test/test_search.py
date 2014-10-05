__author__ = 'tolkjen'

import pytest

from ..search import RemoveSpace, NormalizeSpace, SpaceException
from ..descriptors import PreprocessingDescriptor


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
