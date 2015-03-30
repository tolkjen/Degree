__author__ = 'tolkjen'

from numpy import concatenate
from numpy.random import RandomState
from sklearn.cross_validation import StratifiedKFold


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
            scores = self._cross_validate(classifier, sample.attributes, sample.categories, split)
            total_scores.extend(scores)
        return total_scores

    def _cross_validate(self, clf, attributes, category, splits):
        results = []
        for split in splits:
            training_indices, test_indices = split
            clf.fit(attributes[training_indices], category[training_indices])
            prediction = clf.predict(attributes[test_indices])
            truth = category[test_indices]

            tp, tn, fp, fn = 0, 0, 0, 0
            for i in xrange(len(truth)):
                tp += truth[i] and prediction[i]
                #tn += not truth[i] and not prediction[i]
                fp += not truth[i] and prediction[i]
                fn += truth[i] and not prediction[i]

            precision = float(tp) / (tp + fp)
            sensivity = float(tp) / (tp + fn)
            f1 = 2.0*tp / (2.0*tp + fp + fn)
            results.append([sensivity, precision, f1])
        return results

    def _clone_random_state(self):
        if self._random:
            r = RandomState()
            r.set_state(self._random.get_state())
            return r
        return None
