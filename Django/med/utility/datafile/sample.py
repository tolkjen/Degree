# coding=utf-8
import xlsfile
from transform import StringTransform


class Sample:
    """
    Represents a data sample. Sample contains a list of rows, each having a list of attributes an a category. Each
    attribute is numeric, although they are all stored as strings.
    """

    @staticmethod
    def _is_numeric(x):
        try:
            float(x)
            return True
        except:
            return False

    @staticmethod
    def fromFile(filepath):
        """
        Loads a Sample from a given filepath. Currently only XLS files are supported.
        :param filepath: A path to the file.
        :return: A Sample instance.
        """
        return Sample.fromXls(filepath)

    @staticmethod
    def fromXls(filepath):
        """
        Attempts to create a sample out of XLS file. If a file has no "Index" column, an exception is thrown. If file
        contains columns which contain mostly non-numeric values, those columns are discarded. Each row containing an
        empty value is also discarded.
        :param filepath: File to the file to load sample from.
        :return: A Sample object instance.
        """
        datafile = xlsfile.XlsFile(filepath)
        datafile.read()

        # Look for Index column inside the file
        try:
            category_column_index = [s.lower() for s in datafile.columns()].index('index')
        except:
            raise Exception('Plik nie posiada kolumny o nazwie "Index".')

        # Look for data columns, which mostly contain numeric values
        numericAttrColumns = []
        for i in range(len(datafile.columns())):
            numericCount = 0
            for row in datafile.rows():
                if Sample._is_numeric(row[i]):
                    numericCount += 1
            if numericCount > len(datafile.rows()) / 2 and i != category_column_index:
                numericAttrColumns.append(i)

        sample = Sample()
        sample._attribute_column_count = len(numericAttrColumns)
        if sample._attribute_column_count == 0:
            raise Exception('Plik nie posiada kolumn w których przeważają wartości numeryczne.')

        for row in datafile.rows():
            attributes = [row[i] for i in numericAttrColumns]

            attr_not_empty = reduce(lambda a, b: a and b != '', attributes, True)
            cat_not_empty = row[category_column_index] != ''

            if attr_not_empty and cat_not_empty:
                sample._data_rows.append((attributes, row[category_column_index]))

        return sample

    def __init__(self):
        self._data_rows = []
        self._attribute_column_count = 0

    def rows(self):
        return self._data_rows

    def positive_count(self):
        return sum([1 for (attributes, value) in self._data_rows if value == "1.0"])

    def transform_attributes(self, num_trans):
        column_numeric = [True] * self._attribute_column_count
        for (attributes, value) in self._data_rows:
            for (index, attribute) in enumerate(attributes):
                if column_numeric[index]:
                    column_numeric[index] = Sample._is_numeric(attribute)

        mapper = {True: num_trans, False: StringTransform()}
        transformers = [mapper[is_numeric].clone() for is_numeric in column_numeric]
        for (attributes, value) in self._data_rows:
            for (index, attribute) in enumerate(attributes):
                transformers[index].put(attribute)

        new_rows = []
        for (attributes, value) in self._data_rows:
            new_attributes = [transformers[i].transform(attr) for (i, attr) in enumerate(attributes)]
            new_rows.append((new_attributes, value))
        self._data_rows = new_rows
