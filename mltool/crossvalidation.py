__author__ = 'tolkjen'

from numpy.random import RandomState
from sklearn.cross_validation import cross_val_score, StratifiedKFold


class CrossValidator(object):
    def __init__(self, random_state=None, splits_per_group=3):
        self._random = random_state
        self._iterations = splits_per_group
        self._split_groups = {}

    def validate(self, sample, classifier):
        n_rows = len(sample.attributes)
        if not n_rows in self._split_groups:
            random = self._clone_random_state()
            group = [StratifiedKFold(sample.categories, n_folds=5, shuffle=True, random_state=random) for _ in
                     xrange(self._iterations)]
            self._split_groups[n_rows] = group

        mean_list = []
        split_group = self._split_groups[n_rows]
        for split in split_group:
            scores = cross_val_score(classifier, sample.attributes, sample.categories, cv=split, scoring="f1")
            mean_list.append(scores.mean())
        return sum(mean_list) / float(len(mean_list))

    def _clone_random_state(self):
        if self._random:
            r = RandomState()
            r.set_state(self._random.get_state())
            return r
        return None
