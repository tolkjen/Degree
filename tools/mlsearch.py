__author__ = 'tolkjen'

import sys
import time
import datetime
import argparse

from mltool.spaces import SearchSpace, RemoveSpace, NormalizeSpace, FixSpace, QuantifySpace, ClassificationSpace
from mltool.search import SearchAlgorithm
from tools.datastore import DataStore

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
        search_space = self._create_search_space(args)

        store = DataStore('sqlite:///cache.db')
        if args.reset:
            store.remove(str(search_space))
        elif store.is_done(str(search_space)):
            return None

        size = sum([1 for _ in search_space])
        print 'Size: %d\n' % size

        algorithm = SearchAlgorithm(args.filepath, search_space, args.distrib, int(args.group_size), 
                                    int(args.working_set_size))
        algorithm.start()

        started_dt = datetime.datetime.now()
        total_time_estimate = None
        progress_last = 0
        try:
            while algorithm.running():
                time_d = datetime.datetime.now() - started_dt
                if algorithm.progress() <> progress_last:
                    progress_last = algorithm.progress()
                    total_time_estimate = datetime.timedelta(seconds=time_d.total_seconds()*
                                                             (1.0/progress_last))
                if total_time_estimate:
                    if total_time_estimate > time_d:
                        eta = total_time_estimate - time_d
                    else:
                        eta = datetime.timedelta()
                else:
                    eta = datetime.timedelta(days=99)

                sys.stdout.write("\rProgress: %0.2f%% (ETA: %s)%s" % (100.0 * algorithm.progress(), 
                                                                    eta, ' '*20))
                sys.stdout.flush()
                time.sleep(0.25)

            store.set(str(search_space), '', 0, True)
        except KeyboardInterrupt:
            algorithm.stop()

        sys.stdout.write("\r")

        if algorithm.result():
            result, pair = algorithm.result()
            return MlSearchResult(pair.preprocessing_descriptor, pair.classification_descriptor, result)
        return None

    def _create_search_space(self, args):
        fs = FixSpace(args.fix_methods)
        rs = RemoveSpace(args.remove_cols, [int(x) for x in args.remove_sizes])
        ns = NormalizeSpace(args.normalize_cols, [int(x) for x in args.normalize_sizes])
        cs = ClassificationSpace(args.classifiers, int(args.classify_granularity))
        qs = QuantifySpace(args.quantify_cols,
                           args.quantify_algo,
                           [int(x) for x in args.quantify_sizes],
                           args.quantify_max_cols,
                           int(args.quantify_granularity))
        space = SearchSpace(fs, rs, ns, qs, cs)
        return space

    def _parse_arguments(self):
        parser = argparse.ArgumentParser(
            description="Searches through data preprocessing and data classification parameters in order to find ones "
                        "which maximize the classification accuracy.")
        parser.add_argument("filepath", help="Path to the file containing data.")
        parser.add_argument("classifiers",
                            help="List of classification algorithms that search can use. Supported algorithms: " +
                                 ", ".join(ClassificationSpace.algorithms),
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
        parser.add_argument("-qa", "--quantify-algorithms",
                            help="List of quantification algorithms to use. Supported algorithms: " +
                                 ", ".join(QuantifySpace.algorithms),
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
        parser.add_argument("-d", "--distribution", help="Number of processes which run the search in parallel on local "
                            "machine or 'queue'", default=1, dest="distrib")
        parser.add_argument("-gs", "--group-size", help="Packet size for queue", default=10, dest="group_size")
        parser.add_argument("-ws", "--workingset-size", help="Size of the working set", default=100, dest="working_set_size")
        parser.add_argument('-r', '--reset', help='Resets previously calculated progress', action='store_true', dest='reset')

        return parser.parse_args(self._cmd_args)


if __name__ == "__main__":
    app = MlSearch(sys.argv[1:])

    print ""
    print "Machine Learning Search"
    print "-----------------------"
    print ""

    time_started = datetime.datetime.now()
    results = app.search()
    time_finished = datetime.datetime.now()

    if results:
        print "Best accuracy: %f%s" % (results.accuracy, ' '*30)
        print "Classifier info: %s" % results.classification_d
        print "Preprocessing info: %s" % results.preprocessing_d
    else:
        print "Didn't find anything"

    print '\nTime: %s' % str(time_finished - time_started)
