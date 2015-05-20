__author__ = 'tolkjen'

from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.preprocessing import Imputer
from sklearn.cluster import KMeans, MeanShift

from input.models import Clusterer


class DescriptorException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class QuantizationDescriptor:
    """
    Describes clustering of a selected group of data attributes thus turning 
    them into a single, label attribute.
    """
    def _create_kmeans(self, buckets):
        return KMeans(int(buckets), "random")

    def _create_kmeans_pp(self, buckets):
        return KMeans(int(buckets), "k-means++")

    def _create_mean_shift(self):
        return MeanShift()

    _factories = {
        "k-means": _create_kmeans,
        "k-means++": _create_kmeans_pp,
        "meanshift": _create_mean_shift
    }

    def __init__(self, columns, method, args):
        """
        Descriptor constructor.
        :param columns: List of attribute names which should be turned into a 
        one label attribute using the clustering algorithm.
        :param method: Name of the clustering algorithm.
        :param args: List of clustering algorithm parameters.
        """
        self.columns = columns
        self.quantization_method = method
        self.quantization_args = args

    def create_clusterer(self):
        """
        Returns a clustering algorithm instance.
        """
        return QuantizationDescriptor._factories[self.quantization_method](self, *self.quantization_args)

    def validate(self):
        """
        Make sure the descriptor contents are semanticly correct. Raise a 
        DescriptorException if not.
        """
        if len(self.columns) < 1:
            raise DescriptorException("List of columns used for quantization can't be empty.")

        if not self.quantization_method in QuantizationDescriptor._factories.keys():
            raise DescriptorException("Incorrect quantization method.")

    def __str__(self):
        string_args = [str(arg) for arg in self.quantization_args]
        return "%s: (%s, %s)" % (self.quantization_method.upper(), " ".join(self.columns), " ".join(string_args))

    def copy(self):
        return QuantizationDescriptor(self.columns[:], self.quantization_method, self.quantization_args[:])


class PreprocessingDescriptor:
    """
    Describes the preprocessing phase of the algorithm.
    """
    supported_fix_methods = ["median", "mean"]

    def __init__(self, fix_method="mean", remove=[], normalize=[], q_descriptors=[]):
        self.fix_method = fix_method
        self.removed_columns = remove
        self.normalized_columns = normalize
        self.quantization_descriptors = q_descriptors

    def impute(self, sample):
        """
        Create a Sample imputation model according to the method specified in 
        the descriptor.
        :param sample: Sample instance to create the imputer for.
        :returns: Imputer instance.
        """
        imp = Imputer(missing_values='NaN', strategy=self.fix_method, axis=0)
        imp.fit(sample.attributes)
        return imp

    def cluster(self, sample):
        """
        Creates a clustering model for the sample.
        :param sample: Sample to be clustered.
        :returns: A Clusterer instance.
        """
        clusterer = Clusterer(self.quantization_descriptors)
        clusterer.fit(sample)
        return clusterer

    def validate(self):
        """
        Make sure the descriptor contents are semanticly correct. Raise a 
        DescriptorException if not.
        """
        if not self.fix_method in PreprocessingDescriptor.supported_fix_methods:
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
                                       [d.copy() for d in self.quantization_descriptors])


class ClassificationDescriptor:
    """
    Describes a classification algorithm together with its parameters.
    """

    def _create_gaussian_nb(self, params, sample):
        return GaussianNB()

    def _create_decision_tree(self, params, sample):
        return DecisionTreeClassifier()

    def _create_svc_rbf(self, params, sample):
        try:
            c = float(params[0])
            gamma = float(params[1])
        except:
            raise DescriptorException("Classifier parameters are incorrect.")
        else:
            return SVC(C=c, gamma=gamma, kernel="rbf")

    def _create_svc_linear(self, params, sample):
        try:
            c = float(params[0])
        except:
            raise DescriptorException("Classifier parameters are incorrect.")
        else:
            return LinearSVC(dual=False, C=c)

    def _create_knn(self, params, sample):
        try:
            n = int(params[0])
        except:
            raise DescriptorException("Classifier parameters are incorrect.")
        else:
            return KNeighborsClassifier(n_neighbors=n)

    def _create_random_forest(self, params, sample):
        try:
            n = int(params[0])
            features = int(params[1])
            if not sample is None:
                features = min(len(sample.columns), features)
        except:
            raise DescriptorException("Classifier parameters are incorrect.")
        else:
            return RandomForestClassifier(n_estimators=n, max_features=features)

    def _create_extra_trees(self, params, sample):
        try:
            n = int(params[0])
            features = int(params[1])
            if not sample is None:
                features = min(len(sample.columns), features)
        except:
            raise DescriptorException("Classifier parameters are incorrect.")
        else:
            return ExtraTreesClassifier(n_estimators=n, max_features=features)

    # Each entry is:
    #  - key: name for the classifier
    #  - value: a tuple of (factory method, number of parameters accepted)
    _classifiers = {"bayes": (_create_gaussian_nb, 0),
                    "tree": (_create_decision_tree, 0),
                    "svc_rbf": (_create_svc_rbf, 2),
                    "svc_linear": (_create_svc_linear, 1),
                    "knn": (_create_knn, 1),
                    "random_forest": (_create_random_forest, 2),
                    "extra_trees": (_create_extra_trees, 2)}

    def __init__(self, name, arguments):
        self._name = name
        self._arguments = arguments

    def create_classifier(self, sample=None):
        """
        Returns a classifier instance.
        """
        factory, count = ClassificationDescriptor._classifiers[self._name]
        return factory(self, self._arguments, sample)

    def validate(self):
        """
        Make sure the descriptor contents are semanticly correct. Raise a 
        DescriptorException if not.
        """
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
