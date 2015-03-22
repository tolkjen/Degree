__author__ = 'tolkjen'

import sys
import time
import datetime
import argparse
import pickle
import os

from numpy.random import RandomState

from mltool.spaces import SearchSpace, RemoveSpace, NormalizeSpace, FixSpace, QuantifySpace, ClassificationSpace
from mltool.search import SearchAlgorithm
from mltool.input.xlsfile import XlsFile
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
        self._space = None
        self._store = DataStore('sqlite:///cache.db')
        self._args = self._parse_arguments(cmd_args)
        self.random_state_requested = self._args.random_state

    def update_results(self, score, pair, latest_finished, unfinished_ranges):
        self._store.set(self._space, (score, pair), latest_finished, False, unfinished_ranges)

    def get_test_score(self, preprocessing_descriptor, classification_descriptor, random):
        r = RandomState()
        r.set_state(random.get_state())

        xls = XlsFile(self._args.filepath)
        xls.read()
        sample = preprocessing_descriptor.generate_sample(xls)
        evaluation_sample, test_sample = sample.split(r, test_ratio=float(self._args.test_ratio))

        cls = classification_descriptor.create_classifier(evaluation_sample)
        cls.fit(evaluation_sample.attributes, evaluation_sample.categories)
        return cls.score(test_sample.attributes, test_sample.categories)

    def search(self, random):
        self._space = self._create_search_space(self._args)

        cached_result = None
        if self._args.reset:
            self._store.remove(self._space)
        elif self._store.is_done(self._space):
            eval_score, pair = self._store.get_result(self._space)
            test_score = self._store.get_test_score(self._space)
            return MlSearchResult(pair.preprocessing_descriptor, pair.classification_descriptor, test_score)
        else:
            latest_finished = self._store.get_latest(self._space)
            if latest_finished:
                cached_result = self._store.get_result(self._space)
                unfinished_ranges = self._store.get_ranges(self._space)
                self._space.set_offset(latest_finished, unfinished_ranges)

                if self._args.test:
                    return self.evaluate(None, cached_result, random, save_score=False)

        size = sum([1 for _ in self._space])
        print 'Size: %d\n' % size

        algorithm = SearchAlgorithm(self._args.filepath, self._space, self._args.distrib, int(self._args.group_size), 
                                    int(self._args.working_set_size), float(self._args.test_ratio), random)
        algorithm.register_observer(self)
        algorithm.start()

        started_dt = datetime.datetime.now()
        total_time_estimate = None
        progress_last = 0
        finished = False
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

            finished = True
        except KeyboardInterrupt:
            algorithm.stop()

        sys.stdout.write("\r")

        if finished:
            return self.evaluate(algorithm.result(), cached_result, random, save_score=True)
        return None

    def evaluate(self, current_result, cached_result, random, save_score):
        def better_result(a, b):
            if not a: return b
            if not b: return a
            if a[0] > b[0]:
                return a
            return b

        print 'Evaluating algorithm on the test subset...'
        print ''
        sys.stdout.flush()

        result, pair = better_result(current_result, cached_result)
        test_score = self.get_test_score(pair.preprocessing_descriptor, pair.classification_descriptor, random)
        if save_score:
            self._store.set(self._space, (result, pair), 0, True, [], test_score)
        return MlSearchResult(pair.preprocessing_descriptor, pair.classification_descriptor, test_score)

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

    def _parse_arguments(self, args):
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
        parser.add_argument('-s', '--random-state', help='Generates random state and stores it on disk.', action='store_true', 
                            dest='random_state')
        parser.add_argument('-t', '--test', help='Evaluate the best solution found so far.', action='store_true', 
                            dest='test')
        parser.add_argument('-tr', '--test-ratio', help='The bigger, the bigger the test subset will be', default=0.4, 
                            dest='test_ratio')

        return parser.parse_args(args)


def file_exists(filename):
    return os.path.isfile(os.getcwd() + '/' + filename)


def save_random_state(filename):
    with open(filename, 'w') as f:
        f.write(pickle.dumps(RandomState()))


def load_random_state(filename):
    with open(filename, 'r') as f:
        return pickle.loads(f.read())


if __name__ == "__main__":
    app = MlSearch(sys.argv[1:])

    random_state_filename = 'randomstate'
    if app.random_state_requested or not file_exists(random_state_filename):
        print 'Generating random state...'
        print ''
        save_random_state(random_state_filename)

    time_started = datetime.datetime.now()
    results = app.search(load_random_state(random_state_filename))
    time_finished = datetime.datetime.now()

    if results:
        print "Best accuracy: %f%s" % (results.accuracy, ' '*30)
        print "Classifier info: %s" % results.classification_d
        print "Preprocessing info: %s" % results.preprocessing_d
    else:
        print "Didn't find anything                       "

    print '\nTime: %s' % str(time_finished - time_started)
