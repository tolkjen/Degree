__author__ = 'tolkjen'

import os
import pytest
from numpy import array, array_equiv
from ..descriptors import DescriptorException, QuantizationDescriptor, PreprocessingDescriptor, ClassificationDescriptor
from ..input.sample import Sample
from ..input.xlsfile import XlsFile


def from_current_dir(filename):
    return XlsFile.load(os.path.abspath(os.path.dirname(__file__)) + "/" + filename)


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


def test_pre_descriptor_validate():
    d = PreprocessingDescriptor("mean", [], [], [])
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


def test_class_descriptor_wrong_name():
    description = ClassificationDescriptor("???", [1])
    with pytest.raises(DescriptorException):
        description.validate()


def test_class_descriptor_wrong_arguments():
    description = ClassificationDescriptor("gaussianNB", [1])
    with pytest.raises(DescriptorException):
        description.validate()


def test_class_descriptor_create():
    d = ClassificationDescriptor("bayes", [])
    d.create_classifier()


def test_impute():
    d = PreprocessingDescriptor("mean", [], [], [])
    sample = Sample.from_file(from_current_dir("sample6.xlsx"))
    impute_model = d.impute(sample)
    sample.impute_nan(impute_model)

    assert array_equiv(sample.attributes, [[3], [3], [3], [3], [3]])
