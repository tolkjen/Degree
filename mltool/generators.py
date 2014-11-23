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
        if self._size > 0:
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


class ParameterCombinationGenerator(object):
    def __init__(self, lists):
        self._lists = lists
        self._data = []

    def __iter__(self):
        self._data = []
        self._generate([])
        for combination in self._data:
            yield combination

    def _generate(self, working_set):
        index = len(working_set)
        if index == len(self._lists):
            self._data.append(working_set)
        else:
            space = self._lists[index]
            for value in space:
                self._generate(working_set + [value])


class CombinationGenerator(object):
    """
    Generates object combinations without repeating combination sets.
    """

    def __init__(self, objects, size):
        self._objects = objects
        self._size = size
        self._data = []

    def __iter__(self):
        if self._size > 0:
            self._data = []
            self._generate(self._objects, [])
            for x in self._data:
                yield x

    def _generate(self, objects, working_set):
        if len(working_set) == self._size:
            self._data.append(working_set)
        else:
            for i, obj in enumerate(objects):
                self._generate(objects[i:], working_set + [obj])


class CombinationDistributionGenerator(object):
    def __init__(self, combination, max_sum, max_number):
        self._combination = combination
        self._max_sum = max_sum
        self._max_number = max_number
        self._data = []

    def __iter__(self):
        if self._combination:
            self._data = []
            self._generate(0, [])
            for x in self._data:
                yield x

    def _generate(self, sum_value, working_set):
        index = len(working_set)
        if index == len(self._combination):
            self._data.append(working_set)
        else:
            range_start = 1
            if index > 0 and self._combination[index - 1] == self._combination[index]:
                    range_start = working_set[index - 1]
            max_cols = self._max_columns(self._combination[index])

            for i in xrange(range_start, min(max_cols, self._max_sum - sum_value) + 1):
                self._generate(sum_value + i, working_set + [i])

    def _max_columns(self, clusterer):
        if clusterer == "ed":
            return 1
        return self._max_number


class MultiSubsetGenerator(object):
    def __init__(self, objects, combination, distribution):
        self._objects = objects
        self._distribution = distribution
        self._combination = combination
        self._indices = xrange(len(objects))
        self._data = []

    def __iter__(self):
        if self._objects and self._combination and self._distribution:
            self._data = []
            self._generate([])

            collection = {}
            for datasets in self._data:
                for index, dataset in datasets:
                    dataset.sort()
                datasets.sort()
                collection[str(datasets)] = datasets
            self._data = collection.values()

            for multiset in self._data:
                yield [[self._objects[i] for i in subset] for index, subset in multiset]

    def _generate(self, working_set):
        index = len(working_set)
        if index == len(self._distribution):
            self._data.append(working_set)
        else:
            flat_working_set = reduce(lambda a, b: a + b[1], working_set, [])

            subrange = [i for i in self._indices if not i in flat_working_set]

            if len(subrange) >= self._distribution[index]:
                generator = SubsetGenerator(subrange, self._distribution[index])
                for subset in generator:
                    self._generate(working_set + [(self._combination[index], subset)])
