__author__ = 'tolkjen'


class GeneratorException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class SubsetGenerator(object):
    """
    Generates subsets of a particular size from a given list. If the size is zero, generates one item - empty list.
    """

    def __init__(self, objects, size):
        """
        Creates a SubsetGenerator object.
        :param objects: Object from which subsets will be generated.
        :param size: Size of each generated subset.
        """
        if size > len(objects):
            raise GeneratorException("Subset size can't be bigger than the number of objects.")
        self._objects = objects
        self._size = size
        self._data = []

    def __iter__(self):
        self._data = []
        self._generate(0, [])
        for subset in self._data:
            yield subset

    def _generate(self, index, working_set):
        if index == len(self._objects):
            if len(working_set) == self._size:
                self._data.append(working_set)
        else:
            self._generate(index + 1, working_set)
            self._generate(index + 1, working_set + [self._objects[index]])


class MultiSubsetGenerator(object):
    """
    Generates groups of disjoint subsets from a given object list.
    """

    def __init__(self, objects, counts):
        if sum(counts) > len(objects):
            raise GeneratorException("Given subset size distribution requires more objects than are available.")

        self._objects = objects
        self._counts = counts
        self._data = []

    def __iter__(self):
        self._data = []
        self._generate(0, [])
        for subset in self._data:
            yield subset

    def _generate(self, n, working_set):
        if n == len(self._counts):
            self._data.append(working_set)
        else:
            flat_working_set = reduce(lambda a, b: a + b, working_set, [])
            generator = SubsetGenerator([x for x in self._objects if not x in flat_working_set], self._counts[n])
            for subset in generator:
                self._generate(n + 1, working_set + [subset])


class DistributionGenerator(object):
    """
    Generates sequences of n non-negative integer numbers, each of them is less or equal to max_number and their sum is
    less or equal to max_sum.
    """

    def __init__(self, n, max_number, max_sum):
        if max_number > max_sum:
            raise GeneratorException("Maximum number is sequence can't be greater than the sum of numbers.")

        self._n = n
        self._max_number = max_number
        self._max_sum = max_sum
        self._data = []

    def __iter__(self):
        self._data = []
        self._generate(0, [])
        for sequence in self._data:
            yield sequence

    def _generate(self, nsum, working_set):
        if len(working_set) == self._n:
            self._data.append(working_set)
        else:
            for i in range(min(self._max_sum - nsum, self._max_number) + 1):
                self._generate(nsum + i, working_set + [i])
