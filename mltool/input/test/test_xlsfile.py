__author__ = 'tolkjen'

import os
import pytest

from ..xlsfile import XlsFile


def from_current_dir(filename):
    return os.path.abspath(os.path.dirname(__file__)) + "/" + filename


def test_open_correct_format():
    XlsFile(from_current_dir('empty.xlsx'))


def test_open_wrong_format():
    with pytest.raises(Exception):
        XlsFile(from_current_dir('wrong.format.xls'))


def test_open_non_existing():
    with pytest.raises(Exception):
        XlsFile(from_current_dir('NO-SUCH-FILE.xls'))


def test_read_empty():
    xlsfile = XlsFile(from_current_dir('empty.xlsx'))
    with pytest.raises(Exception):
        xlsfile.read()


def test_read_no_headers():
    xlsfile = XlsFile(from_current_dir('no.header.xlsx'))
    with pytest.raises(Exception):
        xlsfile.read()


def test_row_and_column_count():
    xlsfile = XlsFile(from_current_dir('sample.xlsx'))
    xlsfile.read()
    assert len(xlsfile.columns()) == 3
    assert len(xlsfile.rows()) == 2
