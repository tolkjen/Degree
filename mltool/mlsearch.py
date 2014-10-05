__author__ = 'tolkjen'

import sys
import argparse
from sklearn import cross_validation

from search import SearchSpace, RemoveSpace, NormalizeSpace, FixSpace, QuantifySpace, ClassificationSpace
from input.xlsfile import XlsFile


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

        xls = XlsFile.load(args.filepath)

        fs = FixSpace(args.fix_methods)
        rs = RemoveSpace(args.remove_cols, [int(x) for x in args.remove_sizes])
        ns = NormalizeSpace(args.normalize_cols, [int(x) for x in args.normalize_sizes])
        cs = ClassificationSpace(args.classifiers, int(args.classify_granularity))
        qs = QuantifySpace(args.quantify_cols,
                           args.quantify_algo,
                           [int(x) for x in args.quantify_sizes],
                           args.quantify_max_cols,
                           args.quantify_granularity)
        space = SearchSpace(fs, rs, ns, qs, cs)

        space_size = 0
        for _ in space:
            space_size += 1
        counter = 0

        best_pair = None
        best_result = 0.0

        for pair in space:
            sample = pair.preprocessing_descriptor.generate_sample(xls)
            classifier = pair.classification_descriptor.create_classifier()
            scores = cross_validation.cross_val_score(classifier, sample.attributes, sample.categories, cv=5,
                                                      scoring="f1")

            if scores.mean() > best_result:
                best_result = scores.mean()
                best_pair = pair.copy()

            sys.stdout.write("\rProgress: %0.2f%%" % (100.0 * counter / float(space_size)))
            sys.stdout.flush()
            counter += 1

        sys.stdout.write("\r")

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
        parser.add_argument("-qc", "--quantify-cols", help="List of columns which can be used during quantification.",
                            default=[], dest="quantify_cols", action=MlSearch.SplitAction)
        parser.add_argument("-qa", "--quantify-algorithms", help="List of quantification algorithms to use.",
                            default=[], dest="quantify_algo", action=MlSearch.SplitAction)
        parser.add_argument("-qs", "--quantify-sizes", help="List of numbers of quantifications performed at the same "
                                                            "time.",
                            default=[], dest="quantify_sizes", action=MlSearch.SplitAction)
        parser.add_argument("-qm", help="Maximum number of columns that quantification algorithm can use.",
                            default=3, dest="quantify_max_cols")
        parser.add_argument("-qg", "--qunatify-granularity",
                            help="The level of granularity of iterating over quantification algorithm parameters.",
                            default=5, dest="quantify_granularity")
        parser.add_argument("-cg", "--classification-granularity",
                            help="The level of granularity when iterating over classification parameters.", default=5,
                            dest="classify_granularity")

        return parser.parse_args(self._cmd_args)


if __name__ == "__main__":
    app = MlSearch(sys.argv[1:])

    print ""
    print "Machine Learning Search"
    print "-----------------------"
    print ""

    results = app.search()

    print "Best accuracy: %f" % results.accuracy
    print "Classifier info: %s" % results.classification_d
    print "Preprocessing info: %s" % results.preprocessing_d
