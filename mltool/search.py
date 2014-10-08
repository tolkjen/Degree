__author__ = 'tolkjen'

import threading
import multiprocessing
from sklearn import cross_validation

from input.xlsfile import XlsFile


def _process_entry_point(filepath, q_work, q_result):
    xls = XlsFile(filepath)
    xls.read()

    try:
        q_result.put((0.0, None))
        while True:
            pair = q_work.get()

            sample = pair.preprocessing_descriptor.generate_sample(xls)
            classifier = pair.classification_descriptor.create_classifier()
            scores = cross_validation.cross_val_score(classifier, sample.attributes, sample.categories, cv=5,
                                                      scoring="f1")

            q_result.put((scores.mean(), pair))
    except KeyboardInterrupt:
        q_result.put((0.0, None))


class SearchAlgorithm(object):
    def __init__(self, filepath, search_space, processes=1):
        self._search_space = search_space
        self._processes = processes
        self._filepath = filepath

        self._running = False
        self._running_lock = threading.Lock()
        self._progress_fraction = 0.0
        self._progress_lock = threading.Lock()
        self._stop_requested = False
        self._thread = None
        self._result = (0.0, None)

    def start(self):
        if self._processes == 1:
            self._thread = threading.Thread(target=self._thread_worker_basic)
        else:
            self._thread = threading.Thread(target=self._thread_worker_multiprocess, args=(self._processes, ))

        with self._running_lock:
            self._running = True
        self._thread.start()

    def progress(self):
        with self._progress_lock:
            return self._progress_fraction

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

        space_size = 0
        for _ in self._search_space:
            space_size += 1

        best_pair = None
        best_result = 0.0
        progress = 0
        with self._progress_lock:
            self._progress_fraction = 0

        for pair in self._search_space:
            sample = pair.preprocessing_descriptor.generate_sample(xls)
            classifier = pair.classification_descriptor.create_classifier()
            scores = cross_validation.cross_val_score(classifier, sample.attributes, sample.categories, cv=5,
                                                      scoring="f1")

            if scores.mean() > best_result:
                best_result = scores.mean()
                best_pair = pair.copy()

            progress += 1
            with self._progress_lock:
                self._progress_fraction = progress / float(space_size)
                if self._stop_requested:
                    break

        with self._running_lock:
            self._running = False
            self._result = (best_result, best_pair)

    def _thread_worker_multiprocess(self, process_count):
        space_size = 0
        for _ in self._search_space:
            space_size += 1

        queue_result = multiprocessing.Queue()
        queue_work = multiprocessing.Queue()

        processes = []
        for i in range(process_count):
            p = multiprocessing.Process(target=_process_entry_point, args=(self._filepath, queue_work, queue_result))
            p.start()
            processes.append(p)

        best_pair = None
        best_result = 0.0
        progress = -process_count
        with self._progress_lock:
            self._progress_fraction = 0

        for pair in self._search_space:
            result, dp = queue_result.get()
            queue_work.put(pair)

            if result > best_result:
                best_result = result
                best_pair = dp

            progress += 1
            with self._progress_lock:
                self._progress_fraction = max(0.0, progress / float(space_size))
                if self._stop_requested:
                    break

        for _ in processes:
            result, dp = queue_result.get()
            if result > best_result:
                best_result = result
                best_pair = dp
            progress += 1
            with self._progress_lock:
                self._progress_fraction = max(0.0, progress / float(space_size))
                if self._stop_requested:
                    break

        for p in processes:
            p.terminate()

        with self._running_lock:
            self._running = False
            self._result = (best_result, best_pair)
