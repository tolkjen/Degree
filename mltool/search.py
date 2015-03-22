__author__ = 'tolkjen'

import threading
import multiprocessing
import numpy.random
import time
import os

from math import ceil
from celery import group
from datetime import datetime, timedelta

from crossvalidation import CrossValidator
from input.xlsfile import XlsFile
from tasks import validate, app
from cache import SampleCache

def _process_entry_point(random, filepath, q_work, q_result):
    xls = XlsFile(filepath)
    xls.read()

    cache = SampleCache(5)

    cross_validator = CrossValidator(random, splits_per_group=3)
    try:
        q_result.put((0.0, None))
        while True:
            pair = q_work.get()

            sample = pair.preprocessing_descriptor.generate_sample(xls, cache)
            classifier = pair.classification_descriptor.create_classifier(sample)
            score = cross_validator.validate(sample, classifier)

            q_result.put((score, pair))
    except KeyboardInterrupt:
        q_result.put((0.0, None))


class Progress(object):
    def __init__(self, search_space=None, max=0, value=0):
        self._progress = value
        self._space_size = 0

        if search_space:
            for _ in search_space:
                self._space_size += 1
        else:
            self._space_size = max

    def inc(self, value=1):
        self._progress += value

    def fraction(self):
        return max(0.0, self._progress / float(self._space_size))


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


class SearchAlgorithm(object):
    def __init__(self, filepath, search_space, distribution=1, group_size=10, 
                 working_set_size=100, random=None):
        self._search_space = search_space
        self._distribution = distribution
        self._filepath = filepath

        self._running = False
        self._running_lock = threading.Lock()
        self._progress_fraction = 0.0
        self._progress_lock = threading.Lock()
        self._progress = None
        self._stop_requested = False
        self._thread = None
        self._result = None
        self._random_state = random
        self._task_group_size = group_size
        self._working_set_size = working_set_size
        self._observer = None

    def start(self):
        self._result = None

        if self._distribution == 'queue':
            self._thread = threading.Thread(target=self._thread_worker_celery)
        else:
            try:
                process_count = int(self._distribution)
                if process_count < 1:
                    raise Exception('The number of processes must be greater than 1.')
            except ValueError:
                raise Exception('Specified distribution argument is not \'queue\' or a number')

            if process_count == 1:
                self._thread = threading.Thread(target=self._thread_worker_basic)
            else:
                self._thread = threading.Thread(target=self._thread_worker_multiprocess, args=(process_count, ))

        with self._running_lock:
            self._running = True
        self._thread.start()

    def progress(self):
        with self._progress_lock:
            if self._progress:
                return self._progress.fraction()
            return 0.0

    def register_observer(self, observer):
        self._observer = observer

    def result(self):
        return self._result

    def running(self):
        with self._running_lock:
            return self._running

    def stop(self):
        with self._progress_lock:
            self._stop_requested = True
        self._thread.join()

    def _thread_worker_celery(self):
        def completed_count(t):
            return len([1 for task in t if task.result.state == 'SUCCESS'])

        def tasks_finished(t):
            return completed_count(t) == len(t)

        best_pair = None
        best_result = 0.0

        space_size = sum([1 for _ in self._search_space])
        workitems_count = ceil(float(space_size) / self._task_group_size)
        with self._progress_lock:
            self._progress = Progress(max=workitems_count)

        workitems_depleted = False
        working_set = []
        space_iterator = iter(self._search_space)
        space_item_latest = 0
        space_item_finished = 0
        while not workitems_depleted or len(working_set):
            tasks_finished = []
            new_tasks_ready_found = False
            for task in working_set:
                if task.result.ready():
                    score, pair = task.result.get()
                    if score > best_result:
                        best_pair = pair
                        best_result = score

                    with self._progress_lock:
                        self._progress.inc()

                    tasks_finished.append(task)

                    new_tasks_ready_found = True
                    space_item_finished = max(task.number_begin, space_item_finished)

            if new_tasks_ready_found and self._observer:
                unfinished_ranges = [[t.number_begin, t.number_end] for t in working_set if t.number_end < space_item_finished]
                self._observer.update_results(best_result, best_pair, space_item_finished, unfinished_ranges)

            for task in tasks_finished:
                working_set.remove(task)

            while not workitems_depleted and len(working_set) < self._working_set_size:
                workitem_group = []
                group_number_begin = space_item_latest
                try:
                    for _ in xrange(self._task_group_size):
                        workitem_group.append(space_iterator.next().copy())
                        space_item_latest += 1
                except StopIteration:
                    workitems_depleted = True
                group_number_end = space_item_latest
                new_task = Task(validate.s(self._filepath, self._random_state, workitem_group), 
                                group_number_begin, group_number_end)
                new_task.start()
                working_set.append(new_task)

            if self._stop_requested:
                for task in working_set:
                    task.revoke()
                break

            for task in working_set:
                if task.is_lost(timedelta(minutes=30)):
                    task.retry()

            time.sleep(1)

        if best_result:
            with self._running_lock:
                self._running = False
                self._result = (best_result, best_pair)

    def _thread_worker_basic(self):
        xls = XlsFile(self._filepath)
        xls.read()

        best_pair = None
        best_result = 0.0

        with self._progress_lock:
            self._progress = Progress(self._search_space)

        cross_validator = CrossValidator(self._random_state, splits_per_group=3)

        if self._progress._space_size > 0:
            for pair in self._search_space:
                sample = pair.preprocessing_descriptor.generate_sample(xls)
                classifier = pair.classification_descriptor.create_classifier(sample)
                score = cross_validator.validate(sample, classifier)

                if score > best_result:
                    best_result = score
                    best_pair = pair.copy()

                with self._progress_lock:
                    self._progress.inc()
                    if self._stop_requested:
                        break

        with self._running_lock:
            self._running = False
            self._result = (best_result, best_pair)

    def _thread_worker_multiprocess(self, process_count):
        queue_result = multiprocessing.Queue()
        queue_work = multiprocessing.Queue()

        processes = []
        for i in xrange(process_count):
            p = multiprocessing.Process(target=_process_entry_point,
                                        args=(self._random_state, self._filepath, queue_work, queue_result))
            p.start()
            processes.append(p)

        best_pair = None
        best_result = 0.0

        with self._progress_lock:
            self._progress = Progress(self._search_space, -process_count)

        if self._progress._space_size > 0:
            for pair in self._search_space:
                result, dp = queue_result.get()
                queue_work.put(pair.copy())

                if result > best_result:
                    best_result = result
                    best_pair = dp

                with self._progress_lock:
                    self._progress.inc()
                    if self._stop_requested:
                        break

            with self._progress_lock:
                if not self._stop_requested:
                    for _ in processes:
                        result, dp = queue_result.get()
                        if result > best_result:
                            best_result = result
                            best_pair = dp

                        self._progress.inc()
                        if self._stop_requested:
                            break

        for p in processes:
            p.terminate()

        with self._running_lock:
            self._running = False
            self._result = (best_result, best_pair)
