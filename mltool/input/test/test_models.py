import os
import pytest
from numpy import array, array_equiv

from ..models import Normalizer, Clusterer
from ..xlsfile import XlsFile
from ..sample import Sample, SampleException
from ...descriptors import QuantizationDescriptor


def from_current_dir(filename):
    return XlsFile.load(os.path.abspath(os.path.dirname(__file__)) + "/" + filename)


def test_normalizer():
    sample = Sample.from_file(from_current_dir("sample6.xlsx"))
    n = Normalizer()
    n.fit(sample)
    results = n.transform(sample, ["Age", "Weight"])
    expectation = array([[0.0 , 0.5 , 123],
                         [0.25, 0.0 , 233],
                         [0.5 , 0.25, 444],
                         [0.75, 1.0 , 123],
                         [1.0 , 0.75, 333]])

    assert array_equiv(results, expectation)


def test_clusterer():
    clusterer = Clusterer([QuantizationDescriptor(["Age"], "k-means", [3])])
    sample = Sample.from_file(from_current_dir("sample2.xlsx"))
    clusterer.fit(sample)
    sample.merge(clusterer)

    assert sample.ncols == 1
