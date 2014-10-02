__author__ = 'tolkjen'

from descriptors import PreprocessingDescriptor, QuantizationDescriptor
from generators import SubsetGenerator, DistributionGenerator, MultiSubsetGenerator


class SpaceException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class FixSpace(object):
    def __init__(self, methods):
        if not methods:
            raise SpaceException("At least one fix method must be specified.")
        self._methods = methods

    def generate(self, descriptor):
        for method in self._methods:
            descriptor.fix_method = method
            yield descriptor


class RemoveSpace(object):
    def __init__(self, columns, set_sizes):
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


class NormalizeSpace(object):
    def __init__(self, columns, set_sizes):
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


class QuantifySpace(object):
    def __init__(self, columns, clusterers, clusterer_count_list, max_cols, grit):
        if grit < 2:
            raise SpaceException("Grit can't be less than 2.")

        for count in clusterer_count_list:
            if count > len(clusterers):
                raise SpaceException("Clusterer count %d is greater then the number of clusterers." % count)

        self._columns = columns
        self._clusterers = clusterers
        self._count_list = clusterer_count_list
        self._max_cols = max_cols
        self._grit = grit

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
