__author__ = 'tolkjen'

import math

from descriptors import PreprocessingDescriptor, QuantizationDescriptor, ClassificationDescriptor
from generators import SubsetGenerator, MultiSubsetGenerator, ParameterCombinationGenerator, CombinationGenerator, \
    CombinationDistributionGenerator


class SpaceException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class AbstractValueSpace(object):
    """
    Implements a search space pattern. Allows for searching in a range of values. By changing the granularity of the
    search, user can adjust how precise the search will be.
    """

    def __iter__(self):
        """
        Yields values from the value space. The bigger the granularity, the more values generate() will return
        (although it's not a rule).
        """
        pass


class NominalValueSpace(AbstractValueSpace):
    def __init__(self, values):
        self._values = values
        self.granularity = 0

    def __iter__(self):
        for value in self._values:
            yield value


class LinearValueSpace(AbstractValueSpace):
    def __init__(self, start, end):
        self._start = start
        self._end = end
        self.granularity = 2

    def __iter__(self):
        current = self._start
        increment = (self._end - self._start) / float((self.granularity - 1))
        for i in xrange(self.granularity):
            yield current
            current += increment


class ExpValueSpace(AbstractValueSpace):
    def __init__(self, start, end):
        if start <= 0.0 or end <= 0.0:
            raise SpaceException("The range of exponential value space must contain only positive numbers.")

        self._start = start
        self._end = end
        self.granularity = 2

    def __iter__(self):
        p = math.pow((self._end / float(self._start)), 1.0 / float(self.granularity - 1))
        q = math.log(self._start) / math.log(p)
        current = self._start
        for i in xrange(self.granularity):
            yield current
            current *= p


class AbstractSearchSpace(object):
    """
    Implements a search space pattern. Each search space allows iterating over a set of results. Dividing a total search
    space into a set of smaller search spaces makes it easier to search through.
    """

    def generate(self, descriptor):
        """
        Yields values from the search space. If the space is a part of a bigger search hyperspace (containing many
        search spaces), the values in the current space may depend on other spaces. A descriptor object is passed to the
        method in order to carry information about other spaces.
        :param descriptor: Contains information useful in determining the contents of the search space.
        """
        pass


class FixSpace(AbstractSearchSpace):
    """
    Describes the search space of methods used for removing missing values in data file.
    """

    def __init__(self, methods=["remove"]):
        """
        Creates a space instance.
        :param methods: List of methods for removing missing values.
        """
        if not methods:
            raise SpaceException("At least one fix method must be specified.")
        self._methods = methods

    def generate(self, descriptor):
        for method in self._methods:
            descriptor.fix_method = method
            yield descriptor

    def __str__(self):
        return 'Fix(%s)' % ','.join(self._methods)


class RemoveSpace(AbstractSearchSpace):
    """
    Describes the search space of removing columns from the data file.
    """

    def __init__(self, columns=[], set_sizes=[]):
        """
        Creates a search space object.
        :param columns: A list of columns from which the removed columns will be picked.
        :param set_sizes: A list of numbers of columns to be removed at the same time.
        """
        if columns and not set_sizes:
            raise SpaceException("No subset size specified.")

        for size in set_sizes:
            if size > (len(columns)):
                raise SpaceException("Subset size %d is bigger then columns count." % size)

        self._columns = columns
        self._set_sizes = set_sizes

    def generate(self, descriptor):
        if not self._set_sizes:
            descriptor.removed_columns = []
            yield descriptor

        for size in self._set_sizes:
            if size > len(self._columns):
                continue
            if size == 0:
                descriptor.removed_columns = []
                yield descriptor
            generator = SubsetGenerator(self._columns, size)
            for subset in generator:
                descriptor.removed_columns = subset
                yield descriptor

    def __str__(self):
        args = []
        if self._columns: args.append('columns=%s' % ','.join(self._columns))
        if self._set_sizes: args.append('sizes=%s' % ','.join([str(s) for s in self._set_sizes]))
        if args:
            return 'Remove(%s)' % ', '.join(args)
        return ''


class NormalizeSpace(AbstractSearchSpace):
    """
    Describes the search space of normalizing the columns attributes.
    """

    def __init__(self, columns=[], set_sizes=[]):
        """
        Creates a search space object.
        :param columns: A list of columns from which the normalized columns will be picked.
        :param set_sizes: A list of numbers of columns to be normalized at the same time.
        :returns:
        """
        if columns and not set_sizes:
            raise SpaceException("No subset size specified.")

        for size in set_sizes:
            if size > (len(columns)):
                raise SpaceException("Subset size %d is bigger then columns count." % size)

        self._columns = columns
        self._set_sizes = set_sizes

    def generate(self, descriptor):
        if not self._set_sizes:
            descriptor.normalized_columns = []
            yield descriptor
            return

        columns = [col for col in self._columns if not col in descriptor.removed_columns]
        for size in self._set_sizes:
            if size > len(columns):
                continue
            if size == 0:
                descriptor.normalized_columns = []
                yield descriptor
            generator = SubsetGenerator(columns, size)
            for subset in generator:
                descriptor.normalized_columns = subset
                yield descriptor

    def __str__(self):
        args = []
        if self._columns: args.append('columns=%s' % ','.join(self._columns))
        if self._set_sizes: args.append('sizes=%s' % ','.join([str(s) for s in self._set_sizes]))
        if args:
            return 'Normalize(%s)' % ', '.join(args)
        return ''


class QuantifySpace(AbstractSearchSpace):
    """
    Describes the search space of clustering column groups. Search space iterates over different clusterers, clusterer
    parameters, column groups used for clustering and the number of clusterers working at the same time.
    """

    _param_spaces = {
        "k-means": [NominalValueSpace([2,3,4,5,6])],
        "k-means++": [NominalValueSpace([2,3,4,5,6])],
        "meanshift": []
    }

    algorithms = _param_spaces.keys()

    def __init__(self, columns=[], clusterers=[], clusterer_counts=[], max_cols=None, granularity=2):
        """
        Creates a search space object.
        :param columns: A list of columns to be used during clustering.
        :param clusterers: A list of available clusterer objects which could be used for clustering columns.
        :param clusterer_counts: List containing numbers of clusterers which should be used at the same time.
        :param max_cols: Maximum number of columns that any clusterer can use at any time.
        :param granularity: Determines the size of each clusterer parameter search space.
        """
        if granularity < 2:
            raise SpaceException("Grit can't be less than 2.")

        for clusterer in clusterers:
            if not clusterer in QuantifySpace._param_spaces.keys():
                raise SpaceException("Clusterer %s doesn't exist." % clusterer)

        self._columns = columns
        self._clusterers = clusterers
        self._count_list = clusterer_counts
        self._max_cols = max_cols
        self._granularity = granularity

    def __str__(self):
        if not self._columns or not self._clusterers or not self._count_list:
            return ''
        args = []
        count_list_str = [str(c) for c in self._count_list]
        if self._columns: args.append('columns=%s' % ','.join(self._columns))
        if self._clusterers: args.append('algorithms=%s' % ','.join(self._clusterers))
        if self._count_list: args.append('counts=%s' % ','.join(count_list_str))
        args.append('maxcols=%s' % self._max_cols)
        args.append('granularity=%s' % self._granularity)
        return 'Quantify(%s)' % ', '.join(args)

    def generate(self, descriptor):
        if not self._columns or not self._clusterers or not self._count_list:
            descriptor.quantization_descriptors = []
            yield descriptor

        for clusterer in QuantifySpace._param_spaces:
            for space in QuantifySpace._param_spaces[clusterer]:
                space.granularity = self._granularity

        columns = [col for col in self._columns if not col in descriptor.removed_columns]
        for count in self._count_list:
            # Do not try to use more classifiers than columns
            count_adjusted = min(count, len(columns))

            combination_generator = CombinationGenerator(self._clusterers, count_adjusted)
            for combination in combination_generator:
                parameter_spaces = []
                for clusterer in combination:
                    param_combination_generator = ParameterCombinationGenerator(QuantifySpace._param_spaces[clusterer])
                    parameter_spaces.append([param_comb for param_comb in param_combination_generator])

                distribution_generator = CombinationDistributionGenerator(combination, len(columns), self._max_cols)
                for distribution in distribution_generator:
                    multiset_generator = MultiSubsetGenerator(columns, combination, distribution)
                    for multiset in multiset_generator:
                        param_space_generator = ParameterCombinationGenerator(parameter_spaces)
                        for param_space in param_space_generator:
                            descriptor.quantization_descriptors = []
                            for i in xrange(len(combination)):
                                q_descriptor = QuantizationDescriptor(multiset[i], combination[i], param_space[i])
                                descriptor.quantization_descriptors.append(q_descriptor)
                            yield descriptor


class ClassificationSpace(object):

    _param_spaces = {
        "bayes": [],
        "tree": [],
        "svc_rbf": [ExpValueSpace(0.0001, 10000), ExpValueSpace(0.0001, 10000)],
        "svc_linear": [ExpValueSpace(0.0001, 10000)],
        "knn": [NominalValueSpace([1, 3, 5, 7, 9, 11])],
        "random_forest": [NominalValueSpace([10, 20, 40, 80, 160]), NominalValueSpace([2, 3, 4, 5, 6])],
        "extra_trees": [NominalValueSpace([10, 20, 40, 80, 160]), NominalValueSpace([2, 3, 4, 5, 6])],
    }

    algorithms = _param_spaces.keys()

    def __init__(self, classifiers, granularity):
        for classifier in classifiers:
            if not classifier in ClassificationSpace._param_spaces.keys():
                raise SpaceException("Classifier %s is not supported." % classifier)

        self._classifiers = classifiers
        self._granularity = granularity

    def __str__(self):
        return 'Classification(classifiers=%s, granularity=%d)' % (
            ','.join(self._classifiers), self._granularity)

    def generate(self):
        for classifier in self._classifiers:
            for space in ClassificationSpace._param_spaces[classifier]:
                space.granularity = self._granularity

            generator = ParameterCombinationGenerator(ClassificationSpace._param_spaces[classifier])
            for param_combination in generator:
                yield ClassificationDescriptor(classifier, param_combination)


class DescriptorPair(object):
    def __init__(self, preprocessing, classification):
        self.preprocessing_descriptor = preprocessing
        self.classification_descriptor = classification

    def copy(self):
        return DescriptorPair(self.preprocessing_descriptor.copy(), self.classification_descriptor.copy())

    def __str__(self):
        return 'Preprocessing=%s, Classification=%s' % (
            self.preprocessing_descriptor, self.classification_descriptor)


class SearchSpace(object):
    def __init__(self, fix_space, remove_space, normalize_space, quantify_space, classification_space):
        self._fix_space = fix_space
        self._normalize_space = normalize_space
        self._remove_space = remove_space
        self._quantify_space = quantify_space
        self._classification_space = classification_space
        self._offset = -1
        self._unfinished_ranges = []

    def set_offset(self, offset, unfinished_ranges):
        self._offset = offset
        self._unfinished_ranges = unfinished_ranges

    def __iter__(self):
        counter = 0
        for fd in self._fix_space.generate(PreprocessingDescriptor()):
            for rd in self._remove_space.generate(fd):
                for nd in self._normalize_space.generate(rd):
                    for qd in self._quantify_space.generate(nd):
                        for cd in self._classification_space.generate():
                            do_yield = False
                            if counter > self._offset:
                                do_yield = True
                            elif self._unfinished_ranges and counter == self._unfinished_ranges[0][0]:
                                do_yield = True
                                self._unfinished_ranges[0][0] += 1
                                if self._unfinished_ranges[0][0] > self._unfinished_ranges[0][1]:
                                    self._unfinished_ranges.pop(0)

                            if do_yield:
                                yield DescriptorPair(qd, cd)
                            counter += 1

    def __str__(self):
        args = [str(self._fix_space)]
        if str(self._remove_space) != '': args.append(str(self._remove_space))
        if str(self._normalize_space) != '': args.append(str(self._normalize_space))
        if str(self._quantify_space) != '': args.append(str(self._quantify_space))
        args.append(str(self._classification_space))
        return 'Search(%s)' % ', '.join(args)
