__author__ = 'tolkjen'

from numpy import empty, float64, array, hstack

from xlsfile import XlsFile


class SampleException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def _transform_string_number(x):
    if x is None or x == "":
        return None
    return float(x)


def _is_string(x):
    if x == "":
        return False
    try:
        float(x)
        return False
    except:
        return True


def _read_xls_columns(filepath):
    try:
        xlsfile = XlsFile(filepath)
        xlsfile.read()
    except Exception, e:
        raise SampleException("Can't load data sample: " + e.message)

    category_index = -1
    for index in range(len(xlsfile.columns())):
        if xlsfile.columns()[index].lower() == "index":
            category_index = index
    if category_index == -1:
        raise SampleException("Data sample contains no Index column.")

    column_contains_strings = [False] * len(xlsfile.columns())
    column_contains_none = [False] * len(xlsfile.columns())
    for row in xlsfile.rows():
        is_empty = reduce(lambda accumulated, x: x == "" and accumulated, row, True)
        if not is_empty:
            column_contains_strings = [_is_string(row[i]) or column_contains_strings[i] for i in range(len(row))]
            column_contains_none = [row[i] == "" or column_contains_none[i] for i in range(len(row))]

    if column_contains_strings[category_index] or column_contains_none[category_index]:
        raise SampleException("Index column contains string or empty values.")

    attributes = []
    categories = []
    for row in xlsfile.rows():
        attr = [_transform_string_number(value) for i, value in enumerate(row)
                if i != category_index and not column_contains_strings[i]]
        cat = [_transform_string_number(value) for i, value in enumerate(row)
               if i == category_index][0]
        attributes.append(attr)
        categories.append(cat)

    columns = [col for i, col in enumerate(xlsfile.columns())
               if i != category_index and not column_contains_strings[i]]

    return attributes, columns, categories


def _fix_missing_remove(attributes, categories):
    attribute_buffer = empty((len(attributes), len(attributes[0])), dtype=float64)
    categories_buffer = empty((len(attributes)))
    count = 0
    for i in range(len(attributes)):
        contains_empty = False
        for x in attributes[i]:
            if x is None:
                contains_empty = True
                break
        if not contains_empty:
            attribute_buffer[count] = attributes[i]
            categories_buffer[count] = categories[i]
            count += 1
    return attribute_buffer[:count].copy(), categories_buffer[:count].copy()


class Sample:
    _fix_methods = {"remove": _fix_missing_remove}
    supported_fix_methods = _fix_methods.keys()

    @staticmethod
    def from_file(filepath, missing='remove'):
        if not missing in Sample.supported_fix_methods:
            raise SampleException('Incorrect "missing" argument.')

        attributes, columns, categories = _read_xls_columns(filepath)

        # Check for duplicate headers
        if len(columns) != len(set(columns)):
            raise SampleException('Data file contains duplicate column headers.')

        s = Sample()
        s.columns = columns
        s.attributes, s.categories = Sample._fix_methods[missing](attributes, categories)

        return s

    def __init__(self):
        self.attributes = array([])
        self.columns = []
        self.categories = array([])

    def remove_column(self, column_name):
        index = self._column_index(column_name)
        self.attributes = hstack((self.attributes[:, :index], self.attributes[:, index + 1:]))
        self.columns.remove(column_name)

    def normalize_column(self, column_name, normalize_range=(0.0, 1.0)):
        index = self._column_index(column_name)
        scale_min, scale_max = normalize_range
        maximum = max(self.attributes[:, index])
        minimum = min(self.attributes[:, index])
        self.attributes[:, index] = [scale_min + (x - minimum) / (maximum - minimum) * (scale_max - scale_min)
                                     for x in self.attributes[:, index]]

    def merge_columns(self, column_names, clusterer, new_column_name=None):
        if len(column_names) == 0:
            raise SampleException('List of column names can\'t be empty.')

        try:
            column_indices = [self.columns.index(c) for c in column_names]
        except:
            raise SampleException("Specified column names don't belong to sample's columns.")

        remaining_column_names = [col for col in self.columns if not col in column_names]
        remaining_column_indices = [self.columns.index(col) for col in remaining_column_names]

        if new_column_name is None:
            new_column_name = self._create_new_column_name(column_names)

        remaining = self.attributes[:, remaining_column_indices]

        try:
            merged = clusterer.transform(self.attributes[:, column_indices])
        except Exception, e:
            raise SampleException('Can\'t merge columns: {0}'.format(e))

        self.attributes = hstack((remaining, merged))
        self.columns = remaining_column_names + [new_column_name]

    def _create_new_column_name(self, columns_removed):

        def create_name(x):
            return "Col_{0}".format(x)

        remaining_column_names = [col for col in self.columns if not col in columns_removed]
        i = 0
        while create_name(i) in remaining_column_names:
            i += 1
        return create_name(i)

    def _column_index(self, column_name):
        try:
            return self.columns.index(column_name)
        except:
            raise SampleException("Sample doesn't contain data column '{0}'.".format(column_name))