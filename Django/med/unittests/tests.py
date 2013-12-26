import unittest
from os.path import dirname, realpath

from med.utility.crossvalidator import KCrossValidator
from med.utility.classifier import NaiveClassifier
from med.utility.datafile.xlsfile import XlsFile
from med.utility.datafile.sample import Sample

def make_filepath(filename):
	directory = dirname(realpath(__file__))
	return directory + "/" + filename

class KCrossValidatorTestCase(unittest.TestCase):

	def is_score_in_range(self, score):
		return score >= 0.0 and score <= 1.0

	def test_on_empty_sample(self):
		validator = KCrossValidator(NaiveClassifier, 2)
		self.assertRaises(Exception, validator.validate, [])

	def test_on_one_row(self):
		validator = KCrossValidator(NaiveClassifier, 1)
		sample = [ (['1'], '1') ]
		score = validator.validate(sample)
		self.assertTrue(self.is_score_in_range(score))

	def test_on_one_category(self):
		validator = KCrossValidator(NaiveClassifier, 2)
		sample = [
			(['1'], '1'),
			(['2'], '1'),
			(['3'], '1'),
		]
		score = validator.validate(sample)
		self.assertTrue(self.is_score_in_range(score))

	def test_k_greater_then_sample_length(self):
		validator = KCrossValidator(NaiveClassifier, 2)
		sample = [ (['1'], '1') ]
		score = validator.validate(sample)
		self.assertTrue(self.is_score_in_range(score))

	def test_k_non_positive(self):
		self.assertRaises(Exception, KCrossValidator, NaiveClassifier, 0)
		self.assertRaises(Exception, KCrossValidator, NaiveClassifier, -1)

class XlsFileTestCase(unittest.TestCase):

	def test_open_correct_format(self):
		temp = XlsFile(make_filepath('empty.xlsx'))

	def test_open_wrong_format(self):
		self.assertRaises(Exception, XlsFile, make_filepath('wrong.format.xls'))

	def test_open_non_existing(self):
		self.assertRaises(Exception, XlsFile, make_filepath('NOFILE.xls'))

	def test_read_empty(self):
		xlsfile = XlsFile(make_filepath('empty.xlsx'))
		self.assertRaises(Exception, xlsfile.read)

	def test_read_no_headers(self):
		xlsfile = XlsFile(make_filepath('no.header.xlsx'))
		self.assertRaises(Exception, xlsfile.read)

	def test_row_and_column_count(self):
		xlsfile = XlsFile(make_filepath('sample.xlsx'))
		xlsfile.read()
		self.assertEqual(len(xlsfile.columns()), 3)
		self.assertEqual(len(xlsfile.rows()), 2)

class SampleTestCase(unittest.TestCase):

	def test_from_non_existing(self):
		self.assertRaises(Exception, Sample.fromFile, make_filepath('NOFILE.xls'))

	def test_xls_no_index_column(self):
		self.assertRaises(Exception, Sample.fromFile, make_filepath('no.index.xls'))

	def test_xls_contents(self):
		sample = Sample.fromFile(make_filepath('sample2.xlsx'))
		self.assertEqual(len(sample.rows()), 4)
		data = [
			(['Adam', '1.0'], '1.0'),
			(['Kamil', '2.0'], '1.0'),
			(['Pawel', '3.0'], '2.0'),
			(['Karol', '4.0'], '2.0')
		]
		for (index, row) in enumerate(sample.rows()):
			self.assertEqual(row, data[index])

def suite():
	suites = map(unittest.TestLoader().loadTestsFromTestCase,
		[KCrossValidatorTestCase, XlsFileTestCase, SampleTestCase])
	return unittest.TestSuite(suites)

if __name__ == "__main__":
	runner = unittest.TextTestRunner()
	test_suite = suite()
	runner.run(test_suite)
