__author__ = 'tolkjen'

import os

from ..reportgen import AbstractFactory, ReportGenerator, ReportFile


class TestFactory(AbstractFactory):
    class TestCrossValidator(object):
        def validate(self, sample, classifier):
            return 0.5

    class TestSearchAlgorithm(object):
        def __init__(self, filepath, search_space):
            self._filepath = filepath
            self._search_space = search_space

        def start(self):
            pass

        def running(self):
            return False

        def result(self):
            pair = None
            for p in self._search_space:
                pair = p
            return 0.5, pair

    def create_cross_validator(self):
        return TestFactory.TestCrossValidator()

    def create_search_algorithm(self, filepath, search_space):
        return TestFactory.TestSearchAlgorithm(filepath, search_space)


def from_current_dir(filename):
    return os.path.abspath(os.path.dirname(__file__)) + "/" + filename


def test_report_generator_run():
    generator = ReportGenerator(TestFactory(), from_current_dir("sample.xlsx"))
    results = [x for x in generator.generate()]

    # number of classifiers * (4 + number of clusterers * 2)
    assert len(results) > 0

    report_file = ReportFile(from_current_dir('report_test.xls'))
    report_file.write_report(results)


def test_report_file():
    report_file = ReportFile(from_current_dir('data.xlsx'), False)
    assert report_file.read_report_entry('tree', 'ugh')
    assert not report_file.read_report_entry('tree', 'Not reported yet')
