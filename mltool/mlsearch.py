__author__ = 'tolkjen'

import sys
import argparse
from sklearn import cross_validation

from search import SearchSpace


class MlSearchResult(object):
    def __init__(self, preprocessing_d, classification_d, accuracy):
        self.preprocessing_d = preprocessing_d
        self.classification_d = classification_d
        self.accuracy = accuracy


class MlSearch(object):

    class SplitAction(argparse.Action):
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            super(MlSearch.SplitAction, self).__init__(option_strings, dest, nargs, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, values.split(","))

    def __init__(self, cmd_args):
        self._cmd_args = cmd_args

    def search(self):
        args = self._parse_arguments()

        space = SearchSpace(args.fix_methods,
                            args.remove_cols,
                            [int(x) for x in args.remove_sizes],
                            args.normalize_cols,
                            [int(x) for x in args.normalize_sizes],
                            args.classifiers,
                            int(args.granularity))
        best_pair = None
        best_result = 0.0
        for pair in space:
            sample = pair.preprocessing_descriptor.generate_sample(args.filepath)
            classifier = pair.classification_descriptor.create_classifier()
            scores = cross_validation.cross_val_score(classifier, sample.attributes, sample.categories, cv=5,
                                                      scoring="f1")
            if scores.mean() > best_result:
                best_result = scores.mean()
                best_pair = pair

        return MlSearchResult(best_pair.preprocessing_descriptor, best_pair.classification_descriptor, best_result)

    def _parse_arguments(self):
        parser = argparse.ArgumentParser(
            description="Searches through data preprocessing and data classification parameters in order to find ones "
                        "which maximize the classification accuracy.")
        parser.add_argument("filepath", help="Path to the file containing data.")
        parser.add_argument("classifiers", help="List of classification algorithms that search can use.",
                            action=MlSearch.SplitAction)
        parser.add_argument("-f", "--fix", help="List of methods for fixing missing data that search can choose from.",
                            default=["remove"], action=MlSearch.SplitAction, dest="fix_methods")
        parser.add_argument("-rc", "--remove-cols", help="List of columns which search can remove.", default=[],
                            action=MlSearch.SplitAction, dest="remove_cols")
        parser.add_argument("-rs", "--remove-sizes", help="List of the sizes of groups of columns which can be removed "
                                                          "at the same time.",
                            default=[], action=MlSearch.SplitAction, dest="remove_sizes")
        parser.add_argument("-nc", "--normalize-cols", help="List of columns which search can normalize.", default=[],
                            action=MlSearch.SplitAction, dest="normalize_cols")
        parser.add_argument("-ns", "--normalize-sizes", help="List of the sizes of groups of columns which can be "
                                                             "normalized at the same time.",
                            default=[], action=MlSearch.SplitAction, dest="normalize_sizes")
        parser.add_argument("-g", "--granularity", help="The level of granularity when iterating over classification "
                                                        "parameters.",
                            default=5, dest="granularity")
        return parser.parse_args(self._cmd_args)


if __name__ == "__main__":
    app = MlSearch(sys.argv[1:])

    results = app.search()

    print ""
    print "Machine Learning Search"
    print "-----------------------"
    print ""
    print "Best accuracy: %f" % results.accuracy
    print "Classifier info: %s" % results.classification_d
    print "Preprocessing info: %s" % results.preprocessing_d
