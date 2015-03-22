__author__ = 'tolkjen'

from numpy import concatenate
from numpy.random import RandomState
from sklearn.cross_validation import cross_val_score, StratifiedKFold


class CrossValidator(object):
    def __init__(self, random_state=None, iterations=3):
        self._random = random_state
        self._iterations = iterations
        self._split_groups = {}

    def validate(self, sample, classifier):
        n_rows = len(sample.attributes)
        if not n_rows in self._split_groups:
            random = self._clone_random_state()
            group = [StratifiedKFold(sample.categories, n_folds=10, shuffle=True, random_state=random) for _ in
                     xrange(self._iterations)]
            self._split_groups[n_rows] = group

        total_scores = []
        split_group = self._split_groups[n_rows]
        for split in split_group:
            scores = cross_val_score(classifier, sample.attributes, sample.categories, cv=split, scoring="accuracy")
            total_scores = concatenate((total_scores, scores))
        return total_scores.mean() - 3.0 * total_scores.std()

    def _clone_random_state(self):
        if self._random:
            r = RandomState()
            r.set_state(self._random.get_state())
            return r
        return None
