__author__ = 'tolkjen'

import os
import xlrd
import argparse
import pickle

from time import sleep
from tablib import Dataset

from mltool.search import SearchAlgorithm
from mltool.spaces import *
from mltool.crossvalidation import CrossValidator
from mltool.input.xlsfile import XlsFile
from mltool.input.sample import Sample


class AbstractFactory(object):
    def create_cross_validator(self):
        pass

    def create_search_algorithm(self, filepath, search_space):
        pass


class ReportFactory(AbstractFactory):
    def create_cross_validator(self):
        return CrossValidator(splits_per_group=10)

    def create_search_algorithm(self, filepath, search_space):
        return SearchAlgorithm(filepath, search_space, 8)


class ReportEntry(object):
    def __init__(self, classifier, description, score, preprocessing, classification):
        self.classifier = classifier
        self.description = description
        self.score = score
        self.preprocessing = preprocessing
        self.classification = classification

    def to_table_entry(self):
        return [self.classifier, self.description, self.score, str(self.preprocessing), str(self.classification),
                pickle.dumps(self)]

    @staticmethod
    def from_fable_entry(table_entry):
        return pickle.loads(table_entry[5])


class ReportGenerator(object):
    desc_fix = "Fixing empty values"
    desc_remove = "Removing features"
    desc_normalize = "Normalizing features"
    desc_remove_normalize = "Removing and normalizing features"
    desc_alpha_quantify_i = "Quantification (%s)"
    desc_alpha_quantify_ii = "Remove features & quantification (%s)"
    desc_alpha_quantify_iii = "Remove features (*) & quantification (%s)"
    desc_alpha_quantify_iv = "Normalize features & quantification (%s)"
    desc_alpha_quantify_v = "Normalize features (*) & quantification (%s)"
    desc_alpha_quantify_vi = "Removing, normalizing features & quantification (%s)"
    desc_alpha_quantify_vii = "Removing, normalizing features (*) & quantification (%s)"

    quantification_max_features = 3
    quantification_granularity = 5

    def __init__(self, factory, filepath, granularity=5, report_file=None):
        self._granularity = granularity
        self._filepath = filepath
        self._factory = factory
        self._features = []
        self._file = report_file
        self._report_entries = []

    def generate(self):
        self._report_entries = []
        self._read_feature_names()
        classifier_names = ["tree", "knn", "random_forest", "svc_rbf"]
        for name in classifier_names:
            for data in self._generate_classifier_reports(name):
                yield data

    def _generate_classifier_reports(self, classifier_name):
        fix_report = self._generate_fix_report(classifier_name)
        fix_method = fix_report.preprocessing.fix_method
        yield fix_report

        remove_report = self._generate_remove_report(classifier_name, fix_method)
        removed_columns = remove_report.preprocessing.removed_columns
        yield remove_report

        normalize_report = self._generate_normalize_report(classifier_name, fix_method)
        normalized_columns = normalize_report.preprocessing.normalized_columns
        yield normalize_report

        remove_normalize_report = self._generate_remove_normalize_report(classifier_name, fix_method)
        removed_columns_2 = remove_normalize_report.preprocessing.removed_columns
        normalized_columns_2 = remove_normalize_report.preprocessing.normalized_columns
        yield remove_normalize_report

        clustering_algorithms = ["ed", "k-means", "k-means++"]
        for algorithm in clustering_algorithms:
            yield self._generate_alpha_quantification_report_i(classifier_name, fix_method, algorithm)
            yield self._generate_alpha_quantification_report_ii(classifier_name, fix_method, algorithm)
            yield self._generate_alpha_quantification_report_iii(classifier_name, fix_method, algorithm,
                                                                 removed_columns)
            yield self._generate_alpha_quantification_report_iv(classifier_name, fix_method, algorithm)
            yield self._generate_alpha_quantification_report_v(classifier_name, fix_method, algorithm,
                                                               normalized_columns)
            yield self._generate_alpha_quantification_report_vi(classifier_name, fix_method, algorithm)
            yield self._generate_alpha_quantification_report_vii(classifier_name, fix_method, algorithm,
                                                                 removed_columns_2, normalized_columns_2)

    def _generate_fix_report(self, classifier_name):
        fs = FixSpace(["remove", "average"])
        rs = RemoveSpace()
        ns = NormalizeSpace()
        qs = QuantifySpace()
        cs = ClassificationSpace([classifier_name], self._granularity)
        ss = SearchSpace(fs, rs, ns, qs, cs)

        return self._create_report(classifier_name, ss, self.desc_fix)

    def _generate_remove_report(self, classifier_name, fix_method):
        fs = FixSpace([fix_method])
        rs = RemoveSpace(self._features, range(1, len(self._features)))
        ns = NormalizeSpace()
        qs = QuantifySpace()
        cs = ClassificationSpace([classifier_name], self._granularity)
        ss = SearchSpace(fs, rs, ns, qs, cs)

        return self._create_report(classifier_name, ss, self.desc_remove)

    def _generate_normalize_report(self, classifier_name, fix_method):
        fs = FixSpace([fix_method])
        rs = RemoveSpace()
        ns = NormalizeSpace(self._features, range(1, len(self._features) + 1))
        qs = QuantifySpace()
        cs = ClassificationSpace([classifier_name], self._granularity)
        ss = SearchSpace(fs, rs, ns, qs, cs)

        return self._create_report(classifier_name, ss, self.desc_normalize)

    def _generate_remove_normalize_report(self, classifier_name, fix_method):
        fs = FixSpace([fix_method])
        rs = RemoveSpace(self._features, range(1, len(self._features)))
        ns = NormalizeSpace(self._features, range(1, len(self._features) + 1))
        qs = QuantifySpace()
        cs = ClassificationSpace([classifier_name], self._granularity)
        ss = SearchSpace(fs, rs, ns, qs, cs)

        return self._create_report(classifier_name, ss, self.desc_remove_normalize)

    def _generate_alpha_quantification_report_i(self, classifier_name, fix_method, algorithm):
        fs = FixSpace([fix_method])
        rs = RemoveSpace()
        ns = NormalizeSpace()
        qs = QuantifySpace(self._features, [algorithm], range(1, len(self._features) + 1),
                           self.quantification_max_features, self.quantification_granularity)
        cs = ClassificationSpace([classifier_name], self._granularity)
        ss = SearchSpace(fs, rs, ns, qs, cs)

        return self._create_report(classifier_name, ss, self.desc_alpha_quantify_i % algorithm)

    def _generate_alpha_quantification_report_ii(self, classifier_name, fix_method, algorithm):
        fs = FixSpace([fix_method])
        rs = RemoveSpace(self._features, range(1, len(self._features)))
        ns = NormalizeSpace()
        qs = QuantifySpace(self._features, [algorithm], range(1, len(self._features) + 1),
                           self.quantification_max_features, self.quantification_granularity)
        cs = ClassificationSpace([classifier_name], self._granularity)
        ss = SearchSpace(fs, rs, ns, qs, cs)

        return self._create_report(classifier_name, ss, self.desc_alpha_quantify_ii % algorithm)

    def _generate_alpha_quantification_report_iii(self, classifier_name, fix_method, algorithm, removed_columns):
        fs = FixSpace([fix_method])
        rs = RemoveSpace(removed_columns, [len(removed_columns)])
        ns = NormalizeSpace()
        qs = QuantifySpace(self._features, [algorithm], range(1, len(self._features) + 1),
                           self.quantification_max_features, self.quantification_granularity)
        cs = ClassificationSpace([classifier_name], self._granularity)
        ss = SearchSpace(fs, rs, ns, qs, cs)

        return self._create_report(classifier_name, ss, self.desc_alpha_quantify_iii % algorithm)

    def _generate_alpha_quantification_report_iv(self, classifier_name, fix_method, algorithm):
        fs = FixSpace([fix_method])
        rs = RemoveSpace()
        ns = NormalizeSpace(self._features, range(1, len(self._features) + 1))
        qs = QuantifySpace(self._features, [algorithm], range(1, len(self._features) + 1),
                           self.quantification_max_features, self.quantification_granularity)
        cs = ClassificationSpace([classifier_name], self._granularity)
        ss = SearchSpace(fs, rs, ns, qs, cs)

        return self._create_report(classifier_name, ss, self.desc_alpha_quantify_iv % algorithm)

    def _generate_alpha_quantification_report_v(self, classifier_name, fix_method, algorithm, normalized_columns):
        fs = FixSpace([fix_method])
        rs = RemoveSpace()
        ns = NormalizeSpace(normalized_columns, [len(normalized_columns)])
        qs = QuantifySpace(self._features, [algorithm], range(1, len(self._features) + 1),
                           self.quantification_max_features, self.quantification_granularity)
        cs = ClassificationSpace([classifier_name], self._granularity)
        ss = SearchSpace(fs, rs, ns, qs, cs)

        return self._create_report(classifier_name, ss, self.desc_alpha_quantify_v % algorithm)

    def _generate_alpha_quantification_report_vi(self, classifier_name, fix_method, algorithm):
        fs = FixSpace([fix_method])
        rs = RemoveSpace(self._features, range(1, len(self._features)))
        ns = NormalizeSpace(self._features, range(1, len(self._features) + 1))
        qs = QuantifySpace(self._features, [algorithm], range(1, len(self._features) + 1),
                           self.quantification_max_features, self.quantification_granularity)
        cs = ClassificationSpace([classifier_name], self._granularity)
        ss = SearchSpace(fs, rs, ns, qs, cs)

        return self._create_report(classifier_name, ss, self.desc_alpha_quantify_vi % algorithm)

    def _generate_alpha_quantification_report_vii(self, classifier_name, fix_method, algorithm, removed, normalized):
        fs = FixSpace([fix_method])
        rs = RemoveSpace(removed, [len(removed)])
        ns = NormalizeSpace(normalized, [len(normalized)])
        qs = QuantifySpace(self._features, [algorithm], range(1, len(self._features) + 1),
                           self.quantification_max_features, self.quantification_granularity)
        cs = ClassificationSpace([classifier_name], self._granularity)
        ss = SearchSpace(fs, rs, ns, qs, cs)

        return self._create_report(classifier_name, ss, self.desc_alpha_quantify_vii % algorithm)

    def _create_report(self, classifier_name, ss, description):
        if self._file:
            report_entry = self._file.read_report_entry(classifier_name, description)
            if report_entry:
                self._report_entries.append(report_entry)
                return report_entry

        search = self._factory.create_search_algorithm(self._filepath, ss)
        search.start()
        while search.running():
            sleep(0.1)
        pair = search.result()[1]

        sample = pair.preprocessing_descriptor.generate_sample(XlsFile.load(self._filepath))
        classifier = pair.classification_descriptor.create_classifier(sample)
        cross_validator = self._factory.create_cross_validator()
        value = cross_validator.validate(sample, classifier)

        report_entry = ReportEntry(classifier_name, description, value, pair.preprocessing_descriptor,
                                   pair.classification_descriptor)

        if self._file:
            self._report_entries.append(report_entry)
            self._file.write_report(self._report_entries)

        return report_entry

    def _read_feature_names(self):
        sample = Sample.from_file(XlsFile.load(self._filepath))
        self._features = sample.columns


class ReportFile(object):
    def __init__(self, filepath, writable=True):
        self._filepath = filepath
        self._writable = writable

    def write_report(self, report):
        if self._writable:
            report_file = Dataset()
            report_file.headers = ['Classifier', 'Search', 'Cross-validation score', 'Preprocessing', 'Classification',
                                   'Dump']
            for report_entry in report:
                report_file.append(report_entry.to_table_entry())
            with open(self._filepath, 'wb') as f:
                f.write(report_file.xls)

    def read_report_entry(self, classifier, description):
        if os.path.isfile(self._filepath):
            workbook = xlrd.open_workbook(self._filepath)
            datasheet = workbook.sheet_by_index(0)
            for i in xrange(datasheet.nrows):
                row = [cell.value for cell in datasheet.row(i)]
                if row[0] == classifier and row[1] == description:
                    return ReportEntry.from_fable_entry(row)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="Path to the file containing data.")
    parser.add_argument("-g", help="Granularity", default=5, dest="granularity")
    args = parser.parse_args()

    report_file = ReportFile('report.xls')
    app = ReportGenerator(ReportFactory(), args.filepath, args.granularity, report_file)

    print ""
    print "Report generator"
    print "----------------"
    print ""

    report = []
    for entry in app.generate():
        print entry.classifier, entry.description, entry.score
