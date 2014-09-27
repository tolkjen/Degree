import math
import random


class SubsetGenerator:
    def __init__(self, dataset, subset_count):
        if len(dataset) < 2:
            raise Exception("Dataset must have at least 2 elements.")
        self.dataset = dataset

        if subset_count < 2:
            raise Exception("There must be at least two subsets.")
        if subset_count > len(dataset):
            raise Exception("Subset count can't be bigger then the number of dataset" +
                            " elements.")

        self.subset_count = subset_count
        self.test_subset_length = int(math.ceil(float(len(dataset)) / self.subset_count))


class RangeSubsetGenerator(SubsetGenerator):
    """
    Generates a specified number of ranges for a set of values. The ranges
    are one-next-to-another.
    """

    def generate(self):
        dataset_length = len(self.dataset)
        for range_beginning in xrange(0, dataset_length, self.test_subset_length):
            test = self.dataset[range_beginning: range_beginning + self.test_subset_length]
            training = self.dataset[:range_beginning] + self.dataset[range_beginning + self.test_subset_length:]
            yield {'test': test, 'training': training}


class RandomSubsetGenerator(SubsetGenerator):
    def generate(self):
        dataset_copy = [x for x in self.dataset]
        for i in range(self.subset_count):
            sample_length = min(len(dataset_copy), self.test_subset_length)
            test = random.sample(dataset_copy, sample_length)
            training = [item for item in self.dataset if not item in test]
            dataset_copy = [item for item in dataset_copy if not item in test]

            yield {'test': test, 'training': training}
