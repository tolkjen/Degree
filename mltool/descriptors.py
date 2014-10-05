__author__ = 'tolkjen'

from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

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

    def __str__(self):
        string_args = [str(arg) for arg in self.quantization_args]
        return "%s: (%s, %s)" % (self.quantization_method.upper(), " ".join(self.columns), " ".join(string_args))


class PreprocessingDescriptor:
    def __init__(self, fix_method="remove", remove=[], normalize=[], q_descriptors=[]):
        self.fix_method = fix_method
        self.removed_columns = remove
        self.normalized_columns = normalize
        self.quantization_descriptors = q_descriptors

    def generate_sample(self, tabular_file):
        sample = Sample.from_file(tabular_file, self.fix_method)
        for col_name in self.removed_columns:
            sample.remove_column(col_name)
        for col_name in self.normalized_columns:
            sample.normalize_column(col_name)
        for descriptor in self.quantization_descriptors:
            descriptor.execute(sample)
        return sample

    def validate(self):
        if not self.fix_method in Sample.supported_fix_methods:
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

    def __str__(self):
        return "method: %s, removed: [%s], normalized: [%s], quant: [%s]" \
               % (self.fix_method.upper(), ", ".join(self.removed_columns), ", ".join(self.normalized_columns),
                  ", ".join([str(qd) for qd in self.quantization_descriptors]))

    def copy(self):
        return PreprocessingDescriptor(self.fix_method, self.removed_columns[:], self.normalized_columns[:],
                                       self.quantization_descriptors[:])


class ClassificationDescriptor:
    """
    Describes a classification algorithm together with its parameters.
    """

    def _create_gaussian_nb(self, params):
        return GaussianNB()

    def _create_decision_tree(self, params):
        return DecisionTreeClassifier()

    def _create_svc(self, params):
        try:
            c = float(params[0])
            gamma = float(params[1])
        except:
            raise DescriptorException("Classifier parameters are incorrect.")
        else:
            return SVC(C=c, gamma=gamma)

    # Each entry is:
    #  - key: name for the classifier
    #  - value: a tuple of (factory method, number of parameters accepted)
    _classifiers = {"gaussianNB": (_create_gaussian_nb, 0),
                    "tree": (_create_decision_tree, 0),
                    "svc": (_create_svc, 2)}

    def __init__(self, name, arguments):
        self._name = name
        self._arguments = arguments

    def create_classifier(self):
        factory, count = ClassificationDescriptor._classifiers[self._name]
        return factory(self, self._arguments)

    def validate(self):
        if not self._name in ClassificationDescriptor._classifiers.keys():
            raise DescriptorException("Incorrect classifier name.")

        classifier_type, argument_count = ClassificationDescriptor._classifiers[self._name]
        if len(self._arguments) != argument_count:
            raise DescriptorException(
                "Classifier '{0:s}' requires {1:d} parameters, not {2:d}.".format(self._name, argument_count,
                                                                                  len(self._arguments)))

    def __str__(self):
        string_params = [str(x) for x in self._arguments]
        return "name = %s, params = [%s]" % (self._name.upper(), ", ".join(string_params))

    def copy(self):
        return ClassificationDescriptor(self._name, self._arguments[:])
