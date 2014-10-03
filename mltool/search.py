__author__ = 'tolkjen'

from descriptors import PreprocessingDescriptor, QuantizationDescriptor
from generators import SubsetGenerator, DistributionGenerator, MultiSubsetGenerator


class SpaceException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class AbstractSpace(object):
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


class FixSpace(AbstractSpace):
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


class RemoveSpace(AbstractSpace):
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


class NormalizeSpace(AbstractSpace):
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


class QuantifySpace(AbstractSpace):
    """
    Describes the search space of clustering column groups. Search space iterates over different clusterers, clusterer
    parameters, column groups used for clustering and the number of clusterers working at the same time.
    """

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

        self._columns = columns
        self._clusterers = clusterers
        self._count_list = clusterer_count_list
        self._max_cols = max_cols
        self._granularity = granularity

    def generate(self, descriptor):
        columns = [col for col in self._columns if not col in descriptor.removed_columns]
        columns_count = len(columns)
        for count in self._count_list:
            distribution_generator = DistributionGenerator(count, min(columns_count, self._max_cols), columns_count)
            for distribution in distribution_generator:
                multi_generator = MultiSubsetGenerator(columns, distribution)
                for column_subsets in multi_generator:
                    clusterers_generator = SubsetGenerator(self._clusterers, count)
                    for clusterers in clusterers_generator:
                        descriptor.quantization_descriptors = []
                        for i, clusterer in enumerate(clusterers):
                            q_descr = QuantizationDescriptor(column_subsets[i], clusterer, [])
                            descriptor.quantization_descriptors.append(q_descr)
                        yield descriptor
