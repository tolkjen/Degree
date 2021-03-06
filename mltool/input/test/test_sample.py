__author__ = 'tolkjen'

import os
import pytest
from numpy import array, array_equiv, zeros, nan
from numpy.random import RandomState
from numpy.testing import assert_equal

from ..sample import Sample, SampleException
from ..xlsfile import XlsFile


class TestClusterer:
    def predict(self, attributes):
        row_count, col_count = attributes.shape
        return zeros((row_count, 1))


def from_current_dir(filename):
    return XlsFile.load(os.path.abspath(os.path.dirname(__file__)) + "/" + filename)


def test_no_index_column():
    with pytest.raises(SampleException):
        Sample.from_file(from_current_dir('no.index.xlsx'))


def test_xls_contents():
    sample = Sample.from_file(from_current_dir('sample2.xlsx'))
    expected_attributes = array([[1], [2], [3], [4], [5]])
    expected_categories = array([1, 2, 3, 4, 5])
    expected_columns = ["Age"]
    assert array_equiv(sample.attributes, expected_attributes)
    assert array_equiv(sample.categories, expected_categories)
    assert sample.columns == expected_columns


def test_xls_empty_line():
    sample = Sample.from_file(from_current_dir('empty.line.xlsx'))
    expected_attributes = array([[1], [2], [nan], [3], [4]])
    expected_categories = array([1, 2, nan, 3, 4])
    expected_columns = ["Age"]
    assert_equal(sample.attributes, expected_attributes)
    assert_equal(sample.categories, expected_categories)
    assert sample.columns == expected_columns


def test_from_file_with_indices():
    sample = Sample.from_file(from_current_dir('sample2.xlsx'), [0, 4])
    expected_attributes = array([[1], [5]])
    expected_categories = array([1, 5])
    expected_columns = ["Age"]
    assert array_equiv(sample.attributes, expected_attributes)
    assert array_equiv(sample.categories, expected_categories)
    assert sample.columns == expected_columns


def test_index_column_with_empty_values():
    with pytest.raises(SampleException):
        Sample.from_file(from_current_dir('empty.index.xlsx'))


def test_remove_non_existing_column():
    sample = Sample.from_file(from_current_dir('sample3.xlsx'))
    with pytest.raises(SampleException):
        sample.remove_column('Four')


def test_remove_existing_column():
    sample = Sample.from_file(from_current_dir('sample3.xlsx'))
    sample.remove_column('Two')

    expected_attributes = array([[1, 3], [1, 3]])
    expected_categories = array([0, 0])
    expected_columns = ['One', 'Three']
    assert array_equiv(sample.attributes, expected_attributes)
    assert array_equiv(sample.categories, expected_categories)
    assert sample.columns == expected_columns


def test_normalize_non_existing_column():
    sample = Sample.from_file(from_current_dir('sample2.xlsx'))
    normalizer = sample.get_normalizer()
    with pytest.raises(SampleException):
        sample.normalize(normalizer, ["UGH"])


def test_normalize_existing_column():
    sample = Sample.from_file(from_current_dir('sample2.xlsx'))
    normalizer = sample.get_normalizer((0.0, 1.0))
    sample.normalize(normalizer, ["Age"])

    expected_attributes = array([[0.0], [0.25], [0.5], [0.75], [1.0]])
    expected_categories = array([1, 2, 3, 4, 5])
    expected_columns = ["Age"]
    assert array_equiv(sample.attributes, expected_attributes)
    assert array_equiv(sample.categories, expected_categories)
    assert sample.columns == expected_columns


def test_duplicate_headers():
    with pytest.raises(SampleException):
        Sample.from_file(from_current_dir('duplicate.header.xlsx'))


def test_transform():
    sample = Sample.from_file(from_current_dir('sample3.xlsx'))
    sample.merge_columns(['One', 'Three'], TestClusterer(), 'New')

    expected_attributes = array([[2, 0], [2, 0]])
    expected_categories = array([0, 0])
    expected_columns = ['Two', 'New']
    assert array_equiv(sample.attributes, expected_attributes)
    assert array_equiv(sample.categories, expected_categories)
    assert sample.columns == expected_columns


def test_transform_no_columns():
    sample = Sample.from_file(from_current_dir('sample3.xlsx'))
    with pytest.raises(SampleException):
        sample.merge_columns([], TestClusterer())


def test_transform_not_existing_column():
    sample = Sample.from_file(from_current_dir('sample3.xlsx'))
    with pytest.raises(SampleException):
        sample.merge_columns(['Not-existing-column'], TestClusterer())
