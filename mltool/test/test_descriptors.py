__author__ = 'tolkjen'

import os
import pytest
from numpy import array, array_equiv
from ..descriptors import DescriptorException, QuantizationDescriptor, PreprocessingDescriptor
from ..input.clusterers import KMeansClusterer
from ..input.sample import Sample


def from_current_dir(filename):
    return os.path.abspath(os.path.dirname(__file__)) + "\\" + filename


def test_quant_descriptor_validate():
    d = QuantizationDescriptor(['Col_0'], "k-means", [3])
    d.validate()


def test_quant_descriptor_no_columns():
    d = QuantizationDescriptor([], "k-means", [3])
    with pytest.raises(DescriptorException):
        d.validate()


def test_quant_descriptor_wrong_method():
    d = QuantizationDescriptor(["Col_0"], "????", [3])
    with pytest.raises(DescriptorException):
        d.validate()


def test_quant_descriptor_wrong_args():
    incorrect_args_count = KMeansClusterer.param_count + 1
    incorrect_args = [0] * incorrect_args_count
    d = QuantizationDescriptor(["Col_0"], "k-means", incorrect_args)
    with pytest.raises(DescriptorException):
        d.validate()


def test_quant_descriptor_execute():
    sample = Sample.from_file(from_current_dir("sample.xlsx"))
    descriptor = QuantizationDescriptor(["Age"], "ed", [3])
    descriptor.execute(sample)

    expected_attributes = array([0, 1, 2, 0, 1, 2, 0, 1, 2]).reshape(9, 1)
    assert array_equiv(sample.attributes, expected_attributes)


def test_pre_descriptor_validate():
    d = PreprocessingDescriptor("remove", [], [], [])
    d.validate()


def test_pre_descriptor_wrong_fix():
    d = PreprocessingDescriptor("????", [], [], [])
    with pytest.raises(DescriptorException):
        d.validate()


def test_pre_descriptor_normalize_removed():
    d = PreprocessingDescriptor("????", ["Col"], ["Col"], [])
    with pytest.raises(DescriptorException):
        d.validate()


def test_pre_descriptor_merge_removed():
    q = QuantizationDescriptor(["Col"], "k-means", [3])
    d = PreprocessingDescriptor("????", ["Col"], [], [q])
    with pytest.raises(DescriptorException):
        d.validate()


def test_pre_descriptor_generate_sample():
    q = QuantizationDescriptor(["Weight"], "k-means", [1])
    d = PreprocessingDescriptor(fix_method="remove", remove=["Height"], normalize=["Age"], q_descriptors=[q])
    sample = d.generate_sample(from_current_dir("sample2.xlsx"))

    expected_attributes = array([[0.0, 0], [0.5, 0], [1.0, 0]])
    assert array_equiv(sample.attributes, expected_attributes)
