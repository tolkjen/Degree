import os
import sys
import time
import pickle
import argparse
import threading

from numpy.random import RandomState
from math import ceil
from datetime import datetime, timedelta

from mltool.spaces import *
from mltool.descriptors import *
from data import *
from worker import evaluate, app


class Parser(object):
    """
    Parses command line arguments for this script.
    """
    class SplitAction(argparse.Action):
        """
        Used for turning arguments such as "1,2,3" into lists such as 
        ["1", "2", "3"].
        """
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            super(Parser.SplitAction, self).__init__(option_strings, dest, nargs, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, values.split(","))

    def __init__(self):
        self._parser = argparse.ArgumentParser(
            description="Searches through data preprocessing and data classification parameters.")
        self._parser.add_argument("filepath", help="Path to the file containing data.")
        self._parser.add_argument("classifiers",
                            help="List of classification algorithms that search can use. Supported algorithms: " +
                                 ", ".join(ClassificationSpace.algorithms),
                            action=Parser.SplitAction)
        self._parser.add_argument("-f", "--fix", help="List of methods for fixing missing data that search can choose from.",
                            default=["mean"], action=Parser.SplitAction, dest="fix_methods")
        self._parser.add_argument("-rc", "--remove-cols", help="List of columns which search can remove.", default=[],
                            action=Parser.SplitAction, dest="remove_cols")
        self._parser.add_argument("-rs", "--remove-sizes", help="List of the sizes of groups of columns which can be removed "
                                                          "at the same time.",
                            default=[], action=Parser.SplitAction, dest="remove_sizes")
        self._parser.add_argument("-nc", "--normalize-cols", help="List of columns which search can normalize.", default=[],
                            action=Parser.SplitAction, dest="normalize_cols")
        self._parser.add_argument("-ns", "--normalize-sizes", help="List of the sizes of groups of columns which can be "
                                                             "normalized at the same time.",
                            default=[], action=Parser.SplitAction, dest="normalize_sizes")
        self._parser.add_argument("-qc", "--quantify-cols", help="List of columns which can be used during quantification.",
                            default=[], dest="quantify_cols", action=Parser.SplitAction)
        self._parser.add_argument("-qa", "--quantify-algorithms",
                            help="List of quantification algorithms to use. Supported algorithms: " +
                                 ", ".join(QuantifySpace.algorithms),
                            default=[], dest="quantify_algo", action=Parser.SplitAction)
        self._parser.add_argument("-qs", "--quantify-sizes", help="List of numbers of quantifications performed at the same "
                                                            "time.",
                            default=[], dest="quantify_sizes", action=Parser.SplitAction)
        self._parser.add_argument("-qm", help="Maximum number of columns that quantification algorithm can use.",
                            default=3, dest="quantify_max_cols")
        self._parser.add_argument("-qg", "--qunatify-granularity",
                            help="The level of granularity of iterating over quantification algorithm parameters.",
                            default=5, dest="quantify_granularity")
        self._parser.add_argument("-cg", "--classification-granularity",
                            help="The level of granularity when iterating over classification parameters.", default=5,
                            dest="classify_granularity")
        self._parser.add_argument("-gs", "--group-size", help="Packet size for queue", default=10, dest="group_size")
        self._parser.add_argument("-ws", "--set-size", help="Size of the working set", default=100, dest="set_size")
        self._parser.add_argument('-r', '--reset', help='Resets previously calculated progress', action='store_true', dest='reset')
        self._parser.add_argument('-s', '--store-random', help='Generates random state and stores it on disk.', action='store_true', 
                            dest='random_state')

    def parse(self, arguments):
        """
        Parses given command line arguments and returns an object containing 
        script settings derived from those arguments.
        :param arguments: Command line arguments
        :returns: Object with settings.
        """
        args = self._parser.parse_args(arguments)
        args.group_size = int(args.group_size)
        args.set_size = int(args.set_size)
        return args


class Task(object):
    """
    Represents a piece of work sent to a worker application. Every piece of work
    consists of doing some calculations on a group of descriptor pairs
    (preprocessing and classification descriptors). 
    """
    def __init__(self, signature, number_begin, number_end):
        """
        Creates a Task object.
        :param signature: Celery signature object referring to the work
        :param number_begin: The index of the first descriptor pair in the group.
        :param number_end: The index of the last descriptor pair in the group.
        """
        self.signature = signature
        self.result = None 
        self.number_begin = number_begin
        self.number_end = number_end
        self._started_at = None

    def is_lost(self, timeout):
        """
        Decides wether the execution of the task takes more time than it should.
        :param timeout: Timedelta object specifying the maximum execution duration.
        :returns: True if the task takes more time that the timeout, False 
        otherwise.
        """
        if not self._started_at and self.result.state in ['STARTED', 'FAILED']:
            self._started_at = datetime.now()
        if self._started_at:
            return self._started_at + timeout < datetime.now()
        return False

    def retry(self):
        """
        Stops the current task and starts it again. The task will be removed 
        from the queue but it doesn't mean it will stop executing in the worker
        application.
        """
        self.revoke()
        self.start()

    def revoke(self):
        """
        Stops the current task.
        """
        self.result.revoke()

    def start(self):
        """
        Starts the task.
        """
        self.result = self.signature.delay()


class EvaluationProcedure(object):
    """
    Manages calculation distribution between workers and gathering the work 
    results in a parallel thread.
    """
    def __init__(self, filepath, space, random, group_size, set_size):
        """
        Procedure constructor
        :param filepath: Path to the data file.
        :param space: SearchSpace to explore in calculations.
        :param random: RandomState object.
        :param group_size: How many descriptor pairs will be sent to each 
        worker application in one go.
        :param set_size: Maximum number of groups of descriptors calculated in 
        parallel.
        """
        self._filepath = filepath
        self._space = space
        self._random = random
        self._progress_lock = threading.Lock()
        self._progress = 0
        self._group_size = group_size
        self._set_size = set_size
        self._worker_thread = None
        self._stop_requested = False
        self._stop_request_lock = threading.Lock()
        self._observer = None

    def start(self):
        """
        Starts the procedure.
        """
        self._worker_thread = threading.Thread(target=self._worker_method)
        self._worker_thread.start()

    def stop(self):
        """
        Stops the procedure and waits until it finishes.
        """
        self._set_stop_requested(True)
        self._worker_thread.join()

    def set_observer(self, obj):
        """
        Registers an observer for reacting to new partial results coming in. The 
        observer must implement a update_results(new_scores, latest, 
        unfinished_ranges) method.
        """
        self._observer = obj

    def isdone(self):
        """
        Returns True iff the procedure (calculations) finished.
        """
        with self._stop_request_lock:
            return not self._worker_thread.is_alive() and not self._stop_requested

    def progress(self):
        """
        Returns the overall calculations progress in range [0, 1].
        """
        with self._progress_lock:
            return self._progress

    def _set_progress(self, value):
        with self._progress_lock:
            self._progress = value

    def _set_stop_requested(self, value):
        with self._stop_request_lock:
            self._stop_requested = value

    def _worker_method(self):
        self._set_stop_requested(False)
        self._set_progress(0.0)

        space_size = sum([1 for _ in self._space])
        workitems_count = ceil(float(space_size) / self._group_size)
        workitems_calculated = 0

        workitems_depleted = False
        working_set = []
        space_iterator = iter(self._space)
        space_item_latest = 0
        space_item_finished = 0
        while not workitems_depleted or len(working_set):
            tasks_finished = []
            new_scores = []
            new_tasks_ready_found = False
            for task in working_set:
                if task.result.ready():
                    new_tasks_ready_found = True
                    new_scores.extend(task.result.get())
                    tasks_finished.append(task)
                    space_item_finished = max(task.number_end, space_item_finished)
                    workitems_calculated += 1

            for task in tasks_finished:
                working_set.remove(task)

            if new_tasks_ready_found and self._observer:
                unfinished_ranges = [[t.number_begin, t.number_end] for t in working_set if t.number_end < space_item_finished]
                self._observer.update_results(new_scores, space_item_finished, unfinished_ranges)

            self._set_progress(float(workitems_calculated) / workitems_count)

            while not workitems_depleted and len(working_set) < self._set_size:
                workitem_group = []
                group_number_begin = space_item_latest
                try:
                    for _ in xrange(self._group_size):
                        workitem_group.append(space_iterator.next().copy())
                        space_item_latest += 1
                except StopIteration:
                    workitems_depleted = True
                group_number_end = space_item_latest - 1
                new_task = Task(evaluate.s(self._filepath, self._random, workitem_group), 
                                group_number_begin, group_number_end)
                new_task.start()
                working_set.append(new_task)

            with self._stop_request_lock:
                if self._stop_requested:
                    for task in working_set:
                        task.revoke()
                    break

            for task in working_set:
                if task.is_lost(timedelta(minutes=30)):
                    task.retry()

            time.sleep(1.0)


class TimeLeftEstimator(object):
    """
    Estimates the time left to finish some kind of work.
    """
    def __init__(self):
        self.eta = timedelta(days=99)
        self._started_dt = None
        self._total_time_estimate = None
        self._progress_last = 0

    def start(self):
        """
        Tells the estimator that the work has just started.
        """
        # eta is the time left estimate and is updated in each update() call.
        self.eta = timedelta(days=99)
        self._started_dt = datetime.now()
        self._total_time_estimate = None
        self._progress_last = 0

    def update(self, progress):
        """
        Report the work progress to the estimator.
        :param progress: The progress value from range [0, 1].
        """
        time_d = datetime.now() - self._started_dt
        
        if abs(progress - self._progress_last) > 0.01:
            self._total_time_estimate = timedelta(seconds=time_d.total_seconds()*
                                                           (1.0/progress))
            self._progress_last = progress

        if self._total_time_estimate:
            if self._total_time_estimate > time_d:
                self.eta = self._total_time_estimate - time_d
            else:
                self.eta = timedelta()

    def elapsed(self):
        """
        How much time passed since the work started?
        :returns: timedelta object
        """
        return datetime.now() - self._started_dt


class CalculateApplication(object):
    def __init__(self, arguments, database_url, random_filename='random.bin'):
        """
        Creates an application object.
        :param arguments: List of command line arguments.
        :param database_url: URL to the SQL database backend.
        :param random_filename: Filename of the file with random seed.
        """
        self._random_filename = random_filename
        self._search_space = self._create_search_space(arguments)
        self._datastore = SpaceDataStore(database_url)
        self._random = self._get_random_state()
        self._procedure = EvaluationProcedure(arguments.filepath, self._search_space, 
                                              self._random, arguments.group_size, 
                                              arguments.set_size)
        self._procedure.set_observer(self)

    def reset_space(self):
        """
        Removes a SearchSpace from the database.
        """
        self._datastore.delete(self._search_space)

    def recreate_random_state(self):
        """
        Creates a new file with random seed in it. The seed will be used by
        each worker application.
        """
        self._random = RandomState()
        with open(self._random_filename, 'w') as f:
            f.write(pickle.dumps(self._random))

    def update_results(self, new_scores, latest, unfinished_ranges):
        """
        Callback function. Updates the information about the calculation 
        progress in the database.
        :param new_scores: New partial results of the calculations.
        :param latest: Highest index of the descriptor pair for which the 
        results are available.
        :param unfinished_ranges: List of tuples describing indices ranges 
        of descriptor pairs of unfinished work.
        """
        self._datastore.add_scores(self._search_space, new_scores, latest, unfinished_ranges)

    def run(self):
        """
        Starts the calculate application.
        """
        if not self._datastore.isdone(self._search_space):
            retry_info = self._datastore.get_retry_info(self._search_space)
            if retry_info:
                latest_element, ranges = retry_info
                self._search_space.set_offset(latest_element, ranges)

            time_estimate = TimeLeftEstimator()
            time_estimate.start()

            self._procedure.start()
            try:
                while not self._procedure.isdone():
                    self._report_progress(time_estimate)
                    time.sleep(1.0)
                self._datastore.mark_done(self._search_space)
                self._clear_line(time_estimate)
            except KeyboardInterrupt:
                self._procedure.stop()
        else:
            print 'Results already collected'

    def _report_progress(self, time_estimate):
        progress = self._procedure.progress()
        time_estimate.update(progress)
        sys.stdout.write('\rProgress: %0.2f%%  (ETA: %s)%s' % 
                         (100.0 * progress, time_estimate.eta, ' '*20))
        sys.stdout.flush()

    def _clear_line(self, time_estimate):
        sys.stdout.write('\rFinished! (%s)%s\n' % (time_estimate.elapsed(), ' '*20))
        sys.stdout.flush()

    def _get_random_state(self):
        if os.path.isfile(self._random_filename):
            with open(self._random_filename, 'r') as f:
                return pickle.loads(f.read())
        return RandomState()

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


if __name__ == '__main__':
    parser = Parser()
    arguments = parser.parse(sys.argv[1:])

    app = CalculateApplication(arguments, 'postgresql+psycopg2://guest:guest@localhost/db')

    if arguments.reset:
        app.reset_space()

    if arguments.random_state:
        app.recreate_random_state()

    app.run()
