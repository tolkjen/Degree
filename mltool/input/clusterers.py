__author__ = 'tolkjen'

from sys import maxint
import math
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering


def distance_euclidean(a, b):
    return math.sqrt(sum([(a[i] - b[i]) * (a[i] - b[i]) for i in range(len(a))]))


def distance_square(a, b):
    return sum([(a[i] - b[i]) * (a[i] - b[i]) for i in range(len(a))])


class ClustererException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class AbstractClusterer(object):
    """
    Interface for all clusterers.
    """
    def transform(self, attributes):
        """
        Transforms an array of attribute rows into a single column of values.
        :param attributes: Array of attribute rows (width x height).
        :return: Array of values (1 x height).
        """
        pass


class EqualDistributionClusterer(AbstractClusterer):
    param_count = 1

    def __init__(self, bucket_count):
        if bucket_count < 1:
            raise ClustererException('bucket_count must be a positive number.')
        self._bucket_count = int(bucket_count)

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
        self._bucket_count = int(bucket_count)
        self._initialization = 'random'

    def transform(self, attributes):
        row_count, col_count = attributes.shape
        clusterer = KMeans(self._bucket_count, self._initialization)
        clusterer.fit(attributes)
        return clusterer.predict(attributes).reshape(row_count, 1)


class KMeansPlusPlusClusterer(KMeansClusterer):
    param_count = 1

    def __init__(self, bucket_count):
        super(KMeansPlusPlusClusterer, self).__init__(bucket_count)
        self._initialization = 'k-means++'


class DBScanClusterer(AbstractClusterer):
    param_count = 2

    def __init__(self, eps_ratio, min_samples):
        if eps_ratio < 0.0 or eps_ratio > 1.0:
            raise Exception("eps_ratio parameter must be contained within [0, 1].")

        self._eps_ratio = eps_ratio
        self._min_samples = min_samples

    def transform(self, attributes):
        min_distance = maxint
        max_distance = -maxint - 1
        for i in range(len(attributes) - 1):
            for j in range(len(attributes) - i - 1):
                distance = distance_euclidean(attributes[i], attributes[i+j+1])
                min_distance = min(min_distance, distance)
                max_distance = max(max_distance, distance)

        eps = min_distance + (max_distance - min_distance) * self._eps_ratio

        clusterer = DBSCAN(eps=eps, min_samples=self._min_samples)
        return clusterer.fit_predict(attributes).reshape(attributes.shape[0], 1)


class WardHierarchyClusterer(AbstractClusterer):
    param_count = 1

    def __init__(self, buckets):
        self._buckets = int(buckets)
        self._linkage = "ward"

    def transform(self, attributes):
        clusterer = AgglomerativeClustering(n_clusters=self._buckets, linkage=self._linkage)
        return clusterer.fit_predict(attributes).reshape(attributes.shape[0], 1)


class CompleteHierarchyClusterer(WardHierarchyClusterer):
    param_count = 1

    def __init__(self, buckets):
        super(CompleteHierarchyClusterer, self).__init__(buckets)
        self._linkage = "complete"


class AverageHierarchyClusterer(WardHierarchyClusterer):
    param_count = 1

    def __init__(self, buckets):
        super(AverageHierarchyClusterer, self).__init__(buckets)
        self._linkage = "average"