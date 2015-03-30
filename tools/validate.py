import os
import sys
import time
import pickle
import argparse
import threading

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import StaticPool
from mltool.descriptors import *

Base = declarative_base()

from abc import ABCMeta, abstractmethod
from numpy.random import RandomState
from math import ceil
from datetime import datetime, timedelta

from mltool.spaces import *
from mltool.tasks import validate, app


class Parser(object):
    class SplitAction(argparse.Action):
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
                            default=["remove"], action=Parser.SplitAction, dest="fix_methods")
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
        self._parser.add_argument("-d", "--distribution", help="Number of processes which run the search in parallel on local "
                            "machine or 'queue'", default=1, dest="distrib")
        self._parser.add_argument("-gs", "--group-size", help="Packet size for queue", default=10, dest="group_size")
        self._parser.add_argument("-ws", "--set-size", help="Size of the working set", default=100, dest="set_size")
        self._parser.add_argument('-r', '--reset', help='Resets previously calculated progress', action='store_true', dest='reset')
        self._parser.add_argument('-s', '--store-random', help='Generates random state and stores it on disk.', action='store_true', 
                            dest='random_state')

    def parse(self, arguments):
        args = self._parser.parse_args(arguments)
        args.group_size = int(args.group_size)
        args.set_size = int(args.set_size)
        return args


class SearchOperation(Base):
    __tablename__ = 'spaces'

    id = Column(Integer, primary_key=True)
    space = Column(String)
    space_descr = Column(String)
    latest = Column(Integer)
    unfinished = Column(String)
    done = Column(Boolean)

    score_entries = relationship('SearchSpaceScore', cascade="all, delete-orphan")

class SearchSpaceScore(Base):
    __tablename__ = 'scores'

    id = Column(Integer, primary_key=True)
    space_id = Column(Integer, ForeignKey('spaces.id'))
    scores = Column(String)


class SpaceDataStore(object):
    def __init__(self, dburl):
        engine = create_engine(dburl, echo=False, echo_pool=False, poolclass=StaticPool)
        SearchOperation.metadata.create_all(engine) 
        self._session_factory = sessionmaker(bind=engine)

    def add_scores(self, space, scores, latest, unfinished):
        session = self._session_factory()
        space_obj = session.query(SearchOperation).filter_by(space_descr=str(space)).first()
        if not space_obj:
            space_obj = SearchOperation(space_descr=str(space), space=pickle.dumps(space), done=False)
            session.add(space_obj)
            session.commit()
        space_obj.latest = latest
        space_obj.unfinished = pickle.dumps(unfinished)

        scores_obj = SearchSpaceScore(space_id=space_obj.id)
        scores_obj.scores = pickle.dumps(scores)
        session.add(scores_obj)
        session.commit()

    def get_retry_info(self, space):
        session = self._session_factory()
        space_obj = session.query(SearchOperation).filter_by(space_descr=str(space)).first()
        if space_obj:
            return (space_obj.latest, pickle.loads(space_obj.unfinished))
        return None

    def mark_done(self, space):
        session = self._session_factory()
        space_obj = session.query(SearchOperation).filter_by(space_descr=str(space)).first()
        space_obj.done = True
        session.commit()

    def isdone(self, space):
        session = self._session_factory()
        space_obj = session.query(SearchOperation).filter_by(space_descr=str(space)).first()
        if space_obj:
            return space_obj.done
        return False

    def get_spaces(self):
        session = self._session_factory()
        return [pickle.loads(obj.space) for obj in session.query(SearchOperation).all()]

    def get_scores(self, space=None, id=-1):
        session = self._session_factory()
        if space:
            space_obj = session.query(SearchOperation).filter_by(space_descr=str(space)).first()
        else:
            space_obj = session.query(SearchOperation).filter_by(id=id).first()
        total_scores = []
        for score_obj in space_obj.score_entries:
            total_scores.extend(pickle.loads(score_obj.scores))
        return total_scores

    def delete(self, space):
        session = self._session_factory()
        space_obj = session.query(SearchOperation).filter_by(space_descr=str(space)).first()
        if space_obj:
            session.delete(space_obj)
            session.commit()

    def get_id(self, space):
        session = self._session_factory()
        space_obj = session.query(SearchOperation).filter_by(space_descr=str(space)).first()
        if space_obj:
            return space_obj.id
        return False


class Task(object):
    def __init__(self, signature, number_begin, number_end):
        self.signature = signature
        self.result = None 
        self.number_begin = number_begin
        self.number_end = number_end
        self._started_at = None

    def is_lost(self, timeout):
        if not self._started_at and self.result.state in ['STARTED', 'FAILED']:
            self._started_at = datetime.now()
        if self._started_at:
            return self._started_at + timeout < datetime.now()
        return False

    def retry(self):
        self.revoke()
        self.start()

    def revoke(self):
        self.result.revoke()

    def start(self):
        self.result = self.signature.delay()


class ValidationProcedure(object):
    def __init__(self, filepath, space, random, group_size, set_size):
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
        self._worker_thread = threading.Thread(target=self._worker_method)
        self._worker_thread.start()

    def stop(self):
        self._set_stop_requested(True)
        self._worker_thread.join()

    def set_observer(self, obj):
        self._observer = obj

    def isdone(self):
        with self._stop_request_lock:
            return not self._worker_thread.is_alive() and not self._stop_requested

    def progress(self):
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
                new_task = Task(validate.s(self._filepath, self._random, workitem_group), 
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
    def __init__(self):
        self.eta = timedelta(days=99)
        self._started_dt = None
        self._total_time_estimate = None
        self._progress_last = 0

    def start(self):
        self._started_dt = datetime.now()

    def update(self, progress):
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
        return datetime.now() - self._started_dt


class ValidateApplication(object):
    def __init__(self, arguments, database_url, random_filename='random.bin'):
        self._random_filename = random_filename
        self._search_space = self._create_search_space(arguments)
        self._datastore = SpaceDataStore(database_url)
        self._random = self._get_random_state()
        self._procedure = ValidationProcedure(arguments.filepath, self._search_space, 
                                              self._random, arguments.group_size, 
                                              arguments.set_size)
        self._procedure.set_observer(self)

    def reset_space(self):
        self._datastore.delete(self._search_space)

    def recreate_random_state(self):
        self._random = RandomState()
        with open(self._random_filename, 'w') as f:
            f.write(pickle.dumps(self._random))

    def update_results(self, new_scores, space_item_finished, unfinished_ranges):
        self._datastore.add_scores(self._search_space, new_scores, space_item_finished, unfinished_ranges)

    def run(self):
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

    app = ValidateApplication(arguments, 'postgresql+psycopg2://guest:guest@localhost/db')
    if arguments.reset:
        app.reset_space()

    if arguments.random_state:
        app.recreate_random_state()

    app.run()
