__author__ = 'tolkjen'

from input.sample import Sample
from input.clusterers import KMeansClusterer, KMeansPlusPlusClusterer, EqualDistributionClusterer


class DescriptorException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class QuantizationDescriptor:
    _algorithms = {"k-means": KMeansClusterer, "k-means++": KMeansPlusPlusClusterer,
                   "ed": EqualDistributionClusterer}

    def __init__(self, columns, method, args):
        self.columns = columns
        self.quantization_method = method
        self.quantization_args = args

    def execute(self, sample):
        clusterer = QuantizationDescriptor._algorithms[self.quantization_method](*self.quantization_args)
        sample.merge_columns(self.columns, clusterer)

    def validate(self):
        if len(self.columns) < 1:
            raise DescriptorException("List of columns used for quantization can't be empty.")

        if not self.quantization_method in QuantizationDescriptor._algorithms.keys():
            raise DescriptorException("Incorrect quantization method.")

        clusterer_type = QuantizationDescriptor._algorithms[self.quantization_method]
        if len(self.quantization_args) != clusterer_type.param_count:
            raise DescriptorException(
                "Wrong number of arguments for {0} method: expected {1} not {2}.".format(self.quantization_method,
                                                                                         clusterer_type.param_count,
                                                                                         len(self.quantization_args)))


class PreprocessingDescriptor:
    def __init__(self, fix_method, remove, normalize, q_descriptors):
        self.missing_fix_method = fix_method
        self.removed_columns = remove
        self.normalized_columns = normalize
        self.quantization_descriptors = q_descriptors

    def generate_sample(self, filepath):
        sample = Sample.from_file(filepath, self.missing_fix_method)
        for col_name in self.removed_columns:
            sample.remove_column(col_name)
        for col_name in self.normalized_columns:
            sample.normalize_column(col_name)
        for descriptor in self.quantization_descriptors:
            descriptor.execute(sample)
        return sample

    def validate(self):
        if not self.missing_fix_method in Sample.supported_fix_methods:
            raise DescriptorException("Incorrect value of 'missing_fix_method' attribute.")

        for col in self.normalized_columns:
            if col in self.removed_columns:
                raise DescriptorException("Column {0} is supposed to be removed. It can't be normalized.".format(col))

        for descriptor in self.quantization_descriptors:
            descriptor.validate()
            for col in descriptor.columns:
                if col in self.removed_columns:
                    raise DescriptorException(
                        "Column {0} is supposed to be removed. It can't be used for quantization.".format(col))
