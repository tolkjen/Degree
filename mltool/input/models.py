import numpy as np
from sklearn.cluster import DBSCAN

class Normalizer(object):
    def __init__(self, target=(0, 1)):
        self._target_range = target
        self._model = {}

    def fit(self, sample):
        self._model = {}
        for column in sample.columns:
            index = sample.column_index(column)
            rng = (np.min(sample.attributes[:, index]), np.max(sample.attributes[:, index]))
            self._model[column] = rng

    def transform(self, sample, columns):
        data = sample.attributes
        n_rows, n_cols = data.shape

        def transform_number(x, rng):
            begin, end = rng
            width = end - begin
            target_begin, target_end = self._target_range
            target_width = target_end - target_begin
            return (float(x) - begin) / width * target_width + target_begin

        def case_transform(x, y):
            if sample.columns[x] in columns:
                return transform_number(data[y, x], self._model[sample.columns[x]])
            else:
                return data[y, x]
        
        return np.array([
            np.array([case_transform(x, y) for x in xrange(n_cols)]) 
            for y in xrange(n_rows)
        ])


class Clusterer(object):
    def __init__(self, quantization_descriptors):
        self._models = []
        self._qds = quantization_descriptors

    def fit(self, sample):
        self._models = []
        for qd in self._qds:
            column_indices = [sample.column_index(name) for name in qd.columns]
            clusterer = qd.create_clusterer()
            clusterer.fit(sample.attributes[:, column_indices])
            self._models.append(clusterer)

    def transform(self, sample):
        for model, qd in zip(self._models, self._qds):
            sample.merge_columns(qd.columns, model)
