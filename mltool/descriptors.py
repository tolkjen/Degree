__author__ = 'tolkjen'

from sklearn.naive_bayes import GaussianNB

from input.sample import Sample
from input.clusterers import KMeansClusterer, KMeansPlusPlusClusterer, EqualDistributionClusterer


class DescriptorException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)
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
        self._fix_method = fix_method
        self._removed_columns = remove
        self._normalized_columns = normalize
        self._quantization_descriptors = q_descriptors

    def generate_sample(self, filepath):
        sample = Sample.from_file(filepath, self._fix_method)
        for col_name in self._removed_columns:
            sample.remove_column(col_name)
        for col_name in self._normalized_columns:
            sample.normalize_column(col_name)
        for descriptor in self._quantization_descriptors:
            descriptor.execute(sample)
        return sample

    def validate(self):
        if not self._fix_method in Sample.supported_fix_methods:
            raise DescriptorException("Incorrect value of 'missing_fix_method' attribute.")

        for col in self._normalized_columns:
            if col in self._removed_columns:
                raise DescriptorException("Column {0} is supposed to be removed. It can't be normalized.".format(col))

        for descriptor in self._quantization_descriptors:
            descriptor.validate()
            for col in descriptor.columns:
                if col in self._removed_columns:
                    raise DescriptorException(
                        "Column {0} is supposed to be removed. It can't be used for quantization.".format(col))


class ClassificationDescriptor:
    _classifiers = {"gaussianNB": (GaussianNB, 0)}

    def __init__(self, name, arguments):
        if not name in ClassificationDescriptor._classifiers.keys():
            raise DescriptorException("Incorrect classifier name.")

        classifier_type, argument_count = ClassificationDescriptor._classifiers[name]
        if len(arguments) != argument_count:
            raise DescriptorException(
                "Classifier '{0:s}' requires {1:d} parameters, not {2:d}.".format(name, argument_count, len(arguments)))

        self._name = name
        self._arguments = arguments

    def create_classifier(self):
        classifier_type, argument_count = ClassificationDescriptor._classifiers[self._name]
        return classifier_type(*self._arguments)
