__author__ = 'tolkjen'

import os
from time import sleep
from psutil import Process
from threading import Thread
from datetime import timedelta

from ..spaces import RemoveSpace, NormalizeSpace, FixSpace, ClassificationSpace, QuantifySpace, SearchSpace
from ..search import SearchAlgorithm


def completes_within(func, duration):
    thread = Thread(target=func)
    thread.start()
    thread.join(duration.seconds)
    if thread.is_alive():
        # current_process = Process()
        # for child_process in current_process.children():
        #     child_process.kill()
        return False
    return True


def build_search_space():
    fs = FixSpace(["remove"])
    rs = RemoveSpace([], [])
    ns = NormalizeSpace([], [])
    qs = QuantifySpace([], [], [], 1, 2)
    cs = ClassificationSpace(["tree"], 2)
    return SearchSpace(fs, rs, ns, qs, cs)


def get_data_filepath():
    return os.path.abspath(os.path.dirname(__file__)) + "/" + "sample3.xlsx"


def test_completes_within_success():
    def short_work():
        sleep(1)

    assert completes_within(short_work, timedelta(seconds=10))


def test_completes_within_failure():
    def long_work():
        sleep(1)

    assert not completes_within(long_work, timedelta(microseconds=10))


def test_search_run_1p():
    def work():
        algorithm = SearchAlgorithm(get_data_filepath(), build_search_space(), 1)
        algorithm.start()
        while algorithm.running():
            sleep(0.05)
        value, pair = algorithm.result()
        assert value is not None
        assert pair is not None

    assert completes_within(work, timedelta(seconds=10))


def test_search_stop_1p():
    def work():
        algorithm = SearchAlgorithm(get_data_filepath(), build_search_space(), 1)
        algorithm.start()
        sleep(1)
        algorithm.stop()
        value, pair = algorithm.result()
        assert value is not None
        assert pair is not None

    assert completes_within(work, timedelta(seconds=10))


def test_search_start_4p():
    def work():
        algorithm = SearchAlgorithm(get_data_filepath(), build_search_space(), 4)
        algorithm.start()
        while algorithm.running():
            sleep(0.05)
        value, pair = algorithm.result()
        assert value is not None
        assert pair is not None

    assert completes_within(work, timedelta(seconds=10))


def test_search_stop_4p():
    def work():
        algorithm = SearchAlgorithm(get_data_filepath(), build_search_space(), 4)
        algorithm.start()
        sleep(1)
        algorithm.stop()
        value, pair = algorithm.result()
        assert value is not None
        assert pair is not None

    assert completes_within(work, timedelta(seconds=10))
