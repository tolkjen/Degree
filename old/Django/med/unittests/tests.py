import unittest
from os.path import dirname, realpath

from med.utility.crossvalidator import KCrossValidator
from med.utility.classifier import NaiveClassifier
from med.utility.datafile.xlsfile import XlsFile
from med.utility.datafile.sample import Sample
from med.utility.subsetgenerator import RangeSubsetGenerator, RandomSubsetGenerator
from med.utility.datafile.transform import StandardDeviationFilter


def make_filepath(filename):
    directory = dirname(realpath(__file__))
    return directory + "/" + filename


class SubsetGeneratorTestCase(unittest.TestCase):
    SubsetGeneratorType = None

    def test_empty_dataset(self):
        self.assertRaises(Exception, self.SubsetGeneratorType, [], 1)

    def test_one_element(self):
        self.assertRaises(Exception, self.SubsetGeneratorType, [1], 1)

    def test_subsets_less_than_two(self):
        self.assertRaises(Exception, self.SubsetGeneratorType, [1, 2, 3], 0)
        self.assertRaises(Exception, self.SubsetGeneratorType, [1, 2, 3], 1)

    def test_more_subsets_than_elements(self):
        self.assertRaises(Exception, self.SubsetGeneratorType, [1, 2, 3], 10)


class RangeSubsetGeneratorTestCase(SubsetGeneratorTestCase):
    SubsetGeneratorType = RangeSubsetGenerator

    def test_two_elements(self):
        sg = self.SubsetGeneratorType([1, 2], 2)
        results = [x for x in sg.generate()]
        self.assertEqual(len(results), 2)
        self.assertDictEqual(results[0], {"test": [1], "training": [2]})
        self.assertDictEqual(results[1], {"test": [2], "training": [1]})


class RandomSubsetGeneratorTestCase(SubsetGeneratorTestCase):
    SubsetGeneratorType = RandomSubsetGenerator

    def test_subsets_use_whole_dataset(self):
        dataset = range(20)
        sg = self.SubsetGeneratorType(dataset, 6)
        results = [x for x in sg.generate()]
        results_test = set(reduce(lambda x, y: x + y, [subset["test"] for subset in results], []))
        self.assertEqual(len(dataset), len(results_test))


class KCrossValidatorTestCase(unittest.TestCase):
    def is_score_in_range(self, score):
        return 0.0 <= score <= 1.0

    def test_on_empty_sample(self):
        validator = KCrossValidator(NaiveClassifier, 2)
        self.assertRaises(Exception, validator.validate, [])

    def test_specify_group_selection_type(self):
        KCrossValidator(NaiveClassifier, 2, KCrossValidator.GROUP_SELECTION_RANGE)
        KCrossValidator(NaiveClassifier, 2, KCrossValidator.GROUP_SELECTION_RANDOM)

    def test_on_one_row(self):
        validator = KCrossValidator(NaiveClassifier, 1)
        sample = [(['1'], '1')]
        self.assertRaises(Exception, validator.validate, sample)

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
        sample = [(['1'], '1')]
        self.assertRaises(Exception, validator.validate, sample)

    def test_k_non_positive(self):
        self.assertRaises(Exception, KCrossValidator, NaiveClassifier, 0)
        self.assertRaises(Exception, KCrossValidator, NaiveClassifier, -1)


class XlsFileTestCase(unittest.TestCase):
    def test_open_correct_format(self):
        XlsFile(make_filepath('empty.xlsx'))

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
            (['1.0'], '1.0'),
            (['2.0'], '1.0'),
            (['3.0'], '2.0'),
            (['4.0'], '2.0')
        ]
        for (index, row) in enumerate(sample.rows()):
            self.assertEqual(row, data[index])

    def test_xls_pass_rows_with_empty_fields(self):
        sample = Sample.fromFile(make_filepath('empty.fields.xlsx'))
        self.assertEqual(len(sample.rows()), 3)
        data = [
            (['20.0'], '1.0'),
            (['23.0'], '0.0'),
            (['15.0'], '0.0')
        ]
        for (index, row) in enumerate(sample.rows()):
            self.assertEqual(row, data[index])


class StandardDeviationFilterTestCase(unittest.TestCase):
    def test_01(self):
        data = ['1.0', '1.0', '1.0', '1.0', '1.0', '1.0', '1.0', '1.0', '-10', '10']
        filter = StandardDeviationFilter(1)
        for x in data:
            filter.put(x)
        filtered_data = [filter.transform(x) for x in data]
        self.assertListEqual(['1.0']*10, filtered_data)


def suite():
    suites = map(unittest.TestLoader().loadTestsFromTestCase,
                 [KCrossValidatorTestCase,
                  XlsFileTestCase,
                  SampleTestCase,
                  RangeSubsetGeneratorTestCase,
                  RandomSubsetGeneratorTestCase,
                  StandardDeviationFilterTestCase])
    return unittest.TestSuite(suites)


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)
