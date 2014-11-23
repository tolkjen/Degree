__author__ = 'tolkjen'

import threading
import multiprocessing
import numpy.random

from crossvalidation import CrossValidator
from input.xlsfile import XlsFile


def _process_entry_point(random, filepath, q_work, q_result):
    xls = XlsFile(filepath)
    xls.read()

    cross_validator = CrossValidator(random, splits_per_group=3)
    try:
        q_result.put((0.0, None))
        while True:
            pair = q_work.get()

            sample = pair.preprocessing_descriptor.generate_sample(xls)
            classifier = pair.classification_descriptor.create_classifier(sample)
            score = cross_validator.validate(sample, classifier)

            q_result.put((score, pair))
    except KeyboardInterrupt:
        q_result.put((0.0, None))


class Progress(object):
    def __init__(self, search_space, value=0):
        self._search_space = search_space
        self._progress = value

        self.space_size = 0
        for _ in self._search_space:
            self.space_size += 1

    def inc(self):
        self._progress += 1

    def fraction(self):
        return max(0.0, self._progress / float(self.space_size))


class SearchAlgorithm(object):
    def __init__(self, filepath, search_space, processes=1):
        self._search_space = search_space
        self._processes = processes
        self._filepath = filepath

        self._running = False
        self._running_lock = threading.Lock()
        self._progress_fraction = 0.0
        self._progress_lock = threading.Lock()
        self._progress = None
        self._stop_requested = False
        self._thread = None
        self._result = None

    def start(self):
        self._result = None

        if self._processes == 1:
            self._thread = threading.Thread(target=self._thread_worker_basic)
        else:
            self._thread = threading.Thread(target=self._thread_worker_multiprocess, args=(self._processes, ))

        with self._running_lock:
            self._running = True
        self._thread.start()

    def progress(self):
        with self._progress_lock:
            if self._progress:
                return self._progress.fraction()
            return 0.0

    def result(self):
        return self._result

    def running(self):
        with self._running_lock:
            return self._running

    def stop(self):
        with self._progress_lock:
            self._stop_requested = True
        self._thread.join()

    def _thread_worker_basic(self):
        xls = XlsFile(self._filepath)
        xls.read()

        best_pair = None
        best_result = 0.0

        with self._progress_lock:
            self._progress = Progress(self._search_space)

        cross_validator = CrossValidator(None, splits_per_group=3)

        if self._progress.space_size > 0:
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
        random = numpy.random.RandomState()

        processes = []
        for i in xrange(process_count):
            p = multiprocessing.Process(target=_process_entry_point,
                                        args=(random, self._filepath, queue_work, queue_result))
            p.start()
            processes.append(p)

        best_pair = None
        best_result = 0.0

        with self._progress_lock:
            self._progress = Progress(self._search_space, -process_count)

        if self._progress.space_size > 0:
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
