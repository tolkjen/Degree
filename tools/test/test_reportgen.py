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
    generator = ReportGenerator(TestFactory(), from_current_dir("sample.xlsx"),
                                report_file=ReportFile(from_current_dir('report_test.xls')))
    results = [x for x in generator.generate()]
    assert len(results) > 0


def test_report_file_non_existing():
    report_file = ReportFile(from_current_dir('unknown.xlsx'))
    assert not report_file.read_entry('what', 'ever')


def test_report_file_read():
    report_file = ReportFile(from_current_dir('data.xlsx'))
    assert report_file.read_entry('tree', 'Removing features')
    assert not report_file.read_entry('what', 'ever')
