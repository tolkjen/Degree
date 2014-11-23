__author__ = 'tolkjen'

from sklearn.cross_validation import cross_val_score, StratifiedKFold


class CrossValidator(object):
    def __init__(self, random_state=None, splits_per_group=3):
        self._random = random_state
        self._splits_per_group = splits_per_group
        self._split_groups = {}

    def validate(self, sample, classifier):
        n_samples = len(sample.attributes)
        if not n_samples in self._split_groups:
            group = [StratifiedKFold(sample.categories, n_folds=5, shuffle=True, random_state=self._random) for _ in
                     xrange(self._splits_per_group)]
            self._split_groups[n_samples] = group

        mean_list = []
        split_group = self._split_groups[n_samples]
        for split in split_group:
            scores = cross_val_score(classifier, sample.attributes, sample.categories, cv=split, scoring="f1")
            mean_list.append(scores.mean())
        return sum(mean_list) / float(len(mean_list))
