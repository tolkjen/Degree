__author__ = 'tolkjen'

import pytest
from numpy import array, array_equiv, zeros, arange
from ..clusterers import *


def test_e_distance():
    a = array([-3.0, -4.0])
    b = array([3.0, 4.0])
    assert distance_euclidean(a, b) == 10.0


def test_s_distance():
    a = array([-3.0, -4.0])
    b = array([3.0, 4.0])
    assert distance_square(a, b) == 100.0


def test_edc_multiple_columns():
    clusterer = EqualDistributionClusterer(3)
    attributes = arange(10).reshape(5, 2)
    with pytest.raises(ClustererException):
        clusterer.transform(attributes)


def test_edc_transform():
    clusterer = EqualDistributionClusterer(3)
    attributes = array([1, 4, 7, 2, 5, 8, 3, 6, 9]).reshape(9, 1)
    expected_attributes = array([0, 1, 2, 0, 1, 2, 0, 1, 2]).reshape(9, 1)
    assert array_equiv(clusterer.transform(attributes), expected_attributes)


def test_edc_no_buckets():
    with pytest.raises(ClustererException):
        EqualDistributionClusterer(0)


def test_edc_transform_one_bucket():
    clusterer = EqualDistributionClusterer(1)
    attributes = array([1, 4, 7, 2, 5, 8, 3, 6, 9]).reshape(9, 1)
    expected_attributes = zeros((9, 1))
    assert array_equiv(clusterer.transform(attributes), expected_attributes)


def test_edc_transform_too_many_buckets():
    clusterer = EqualDistributionClusterer(10)
    with pytest.raises(ClustererException):
        clusterer.transform(zeros((5, 1)))


def test_km_no_buckets():
    with pytest.raises(ClustererException):
        KMeansClusterer(0)


def test_km_transform():
    clusterer = KMeansClusterer(3)
    data_one_dim = array([1, 2, 3, 10, 11, 12, 101, 102, 103]).reshape(9, 1)
    clusterer.transform(data_one_dim)

    data_two_dim = array([[0, 0], [0, 1], [10, 11], [11, 12], [100, 100], [101, 99]])
    clusterer.transform(data_two_dim)


def test_kmpp_no_buckets():
    with pytest.raises(ClustererException):
        KMeansPlusPlusClusterer(0)


def test_kmpp_transform():
    clusterer = KMeansPlusPlusClusterer(3)
    data_one_dim = array([1, 2, 3, 10, 11, 12, 101, 102, 103]).reshape(9, 1)
    clusterer.transform(data_one_dim)

    data_two_dim = array([[0, 0], [0, 1], [10, 11], [11, 12], [100, 100], [101, 99]])
    clusterer.transform(data_two_dim)