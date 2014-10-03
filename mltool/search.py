__author__ = 'tolkjen'

import math

from descriptors import PreprocessingDescriptor, QuantizationDescriptor
from generators import SubsetGenerator, DistributionGenerator, MultiSubsetGenerator


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


def combinations(value_spaces):
    """
    Generates combinations from values supplied by given value spaces. The number of values may depend on
    granularity.
    :param value_spaces: List of value spaces used to create combinations.
    :param granularity: Granularity for each of the value space.
    """
    data = []
    _generate_combinations(value_spaces, data, [])
    for combination in data:
        yield combination


def _generate_combinations(value_spaces, data, working_set):
    index = len(working_set)
    if index == len(value_spaces):
        data.append(working_set)
    else:
        space = value_spaces[index]
        for value in space:
            _generate_combinations(value_spaces, data, working_set + [value])


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
        for i in range(self.granularity):
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
        for i in range(self.granularity):
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

    def __init__(self, methods):
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


class RemoveSpace(AbstractSearchSpace):
    """
    Describes the search space of removing columns from the data file.
    """

    def __init__(self, columns, set_sizes):
        """
        Creates a search space object.
        :param columns: A list of columns from which the removed columns will be picked.
        :param set_sizes: A list of numbers of columns to be removed at the same time.
        """
        if not set_sizes:
            raise SpaceException("No subset size specified.")

        for size in set_sizes:
            if size > (len(columns)):
                raise SpaceException("Subset size %d is bigger then columns count." % size)

        self._columns = columns
        self._set_sizes = set_sizes

    def generate(self, descriptor):
        for size in self._set_sizes:
            if size > len(self._columns):
                continue
            generator = SubsetGenerator(self._columns, size)
            for subset in generator:
                descriptor.removed_columns = subset
                yield descriptor


class NormalizeSpace(AbstractSearchSpace):
    """
    Describes the search space of normalizing the columns attributes.
    """

    def __init__(self, columns, set_sizes):
        """
        Creates a search space object.
        :param columns: A list of columns from which the normalized columns will be picked.
        :param set_sizes: A list of numbers of columns to be normalized at the same time.
        :return:
        """
        if not set_sizes:
            raise SpaceException("No subset size specified.")

        for size in set_sizes:
            if size > (len(columns)):
                raise SpaceException("Subset size %d is bigger then columns count." % size)

        self._columns = columns
        self._set_sizes = set_sizes

    def generate(self, descriptor):
        columns = [col for col in self._columns if not col in descriptor.removed_columns]
        for size in self._set_sizes:
            if size > len(columns):
                continue
            generator = SubsetGenerator(columns, size)
            for subset in generator:
                descriptor.normalized_columns = subset
                yield descriptor


class QuantifySpace(AbstractSearchSpace):
    """
    Describes the search space of clustering column groups. Search space iterates over different clusterers, clusterer
    parameters, column groups used for clustering and the number of clusterers working at the same time.
    """

    _param_spaces = {
        "k-means": [LinearValueSpace(2, 20)],
        "k-means++": [LinearValueSpace(2, 20)],
        "ed": [LinearValueSpace(2, 20)]
    }

    def __init__(self, columns, clusterers, clusterer_count_list, max_cols, granularity):
        """
        Creates a search space object.
        :param columns: A list of columns to be used during clustering.
        :param clusterers: A list of available clusterer objects which could be used for clustering columns.
        :param clusterer_count_list: List containing numbers of clusterers which should be used at the same time.
        :param max_cols: Maximum number of columns that any clusterer can use at any time.
        :param granularity: Determines the size of each clusterer parameter search space.
        """
        if granularity < 2:
            raise SpaceException("Grit can't be less than 2.")

        for count in clusterer_count_list:
            if count > len(clusterers):
                raise SpaceException("Clusterer count %d is greater then the number of clusterers." % count)

        for clusterer in clusterers:
            if not clusterer in QuantifySpace._param_spaces.keys():
                raise SpaceException("Clusterer %s doesn't exist." % clusterer)

        self._columns = columns
        self._clusterers = clusterers
        self._count_list = clusterer_count_list
        self._max_cols = max_cols
        self._granularity = granularity

    def generate(self, descriptor):
        for clusterer in QuantifySpace._param_spaces:
            for space in QuantifySpace._param_spaces[clusterer]:
                space.granularity = self._granularity

        columns = [col for col in self._columns if not col in descriptor.removed_columns]
        columns_count = len(columns)

        for count in self._count_list:
            distribution_generator = DistributionGenerator(count, min(columns_count, self._max_cols), columns_count)
            for distribution in distribution_generator:
                multi_generator = MultiSubsetGenerator(columns, distribution)
                for column_subsets in multi_generator:
                    clusterers_generator = SubsetGenerator(self._clusterers, count)
                    for clusterers in clusterers_generator:
                        param_space_groups = []
                        for clusterer in clusterers:
                            param_space_groups.append([x for x in combinations(QuantifySpace._param_spaces[clusterer])])

                        for param_space_comb in combinations(param_space_groups):
                            descriptor.quantization_descriptors = []
                            for i, clusterer in enumerate(clusterers):
                                q_descr = QuantizationDescriptor(column_subsets[i], clusterer, param_space_comb[i])
                                descriptor.quantization_descriptors.append(q_descr)
                            yield descriptor
