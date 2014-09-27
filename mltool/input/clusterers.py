__author__ = 'tolkjen'

import sys
import math
import random
from numpy import array
from sklearn.cluster import KMeans


def distance_euclidean(a, b):
    return math.sqrt(sum([(a[i] - b[i]) * (a[i] - b[i]) for i in range(len(a))]))


def distance_square(a, b):
    return sum([(a[i] - b[i]) * (a[i] - b[i]) for i in range(len(a))])


class ClustererException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class AbstractClusterer:
    def transform(self, attributes):
        pass


class EqualDistributionClusterer(AbstractClusterer):
    param_count = 1

    def __init__(self, bucket_count):
        if bucket_count < 1:
            raise ClustererException('bucket_count must be a positive number.')
        self._bucket_count = bucket_count

    def transform(self, attributes):
        row_count, col_count = attributes.shape
        if col_count != 1:
            raise ClustererException('EqualDistributionClusterer can\'t transform multi-column data.')

        if self._bucket_count > row_count:
            raise ClustererException('Can\'t create more clusters than rows.')

        data = attributes[:, 0]

        data_sorted = data.copy()
        data_sorted.sort()
        bucket_size = row_count / self._bucket_count
        bucket_edges = [(data_sorted[bucket_size * i - 1] + data_sorted[bucket_size * i]) / 2.0
                        for i in range(1, self._bucket_count)]
        bucket_edges.append(data_sorted[-1])

        for i in range(len(data)):
            for j, edge in enumerate(bucket_edges):
                if data[i] <= edge:
                    data[i] = j
                    break

        return data.copy().reshape(row_count, 1)


class KMeansClusterer(AbstractClusterer):
    param_count = 1

    def __init__(self, bucket_count):
        if bucket_count < 1:
            raise ClustererException('bucket_count must be a positive number.')
        self._bucket_count = bucket_count
        self._initialization = 'random'

    def transform(self, attributes):
        row_count, col_count = attributes.shape
        clusterer = KMeans(self._bucket_count, self._initialization)
        clusterer.fit(attributes)
        return clusterer.predict(attributes).reshape(row_count, 1)


class KMeansPlusPlusClusterer(KMeansClusterer):
    param_count = 1

    def __init__(self, bucket_count):
        if bucket_count < 1:
            raise ClustererException('bucket_count must be a positive number.')
        self._bucket_count = bucket_count
        self._initialization = 'k-means++'