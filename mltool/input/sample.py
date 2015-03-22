__author__ = 'tolkjen'

from numpy import empty, float64, array, hstack, concatenate
from numpy.random import RandomState

from xlsfile import XlsFile
from sklearn.cross_validation import ShuffleSplit

class SampleException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)
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


def _read_tabular_data(tabular_file):
    """
    Reads a XLS file and produces an array of attributes, column names and categories. All columns containing string
    values are removed. The file must contain a column with "Index" header. Numerical values are converted to float,
    empty values to None.
    :param filepath: A path to the file.
    :return: A tuple of (attributes, column names, categories).
    """
    category_index = -1
    for index in xrange(len(tabular_file.columns())):
        if tabular_file.columns()[index].lower() == "index":
            category_index = index
    if category_index == -1:
        raise SampleException("Data sample contains no Index column.")

    column_contains_strings = [False] * len(tabular_file.columns())
    column_contains_none = [False] * len(tabular_file.columns())
    for row in tabular_file.rows():
        is_empty = reduce(lambda accumulated, x: x == "" and accumulated, row, True)
        if not is_empty:
            column_contains_strings = [_is_string(row[i]) or column_contains_strings[i] for i in xrange(len(row))]
            column_contains_none = [row[i] == "" or column_contains_none[i] for i in xrange(len(row))]

    if column_contains_strings[category_index] or column_contains_none[category_index]:
        raise SampleException("Index column contains string or empty values.")

    attributes = []
    categories = []
    for row in tabular_file.rows():
        attr = [_transform_string_number(value) for i, value in enumerate(row)
                if i != category_index and not column_contains_strings[i]]
        cat = [_transform_string_number(value) for i, value in enumerate(row)
               if i == category_index][0]
        attributes.append(attr)
        categories.append(cat)

    columns = [col for i, col in enumerate(tabular_file.columns())
               if i != category_index and not column_contains_strings[i]]

    return attributes, columns, categories


def _fix_missing_remove(attributes, categories):
    """
    Handles attribute rows with missing values by removing those rows.
    :param attributes: Array of attributes.
    :param categories: Array of categories.
    :return: A tuple of transformed (attributes, categories).
    """
    attribute_buffer = empty((len(attributes), len(attributes[0])), dtype=float64)
    categories_buffer = empty((len(attributes)))
    count = 0
    for i in xrange(len(attributes)):
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


def _fix_missing_average(attributes, categories):
    n_features = len(attributes[0])
    n_rows = len(attributes)

    attribute_buffer = empty((n_rows, n_features), dtype=float64)
    categories_buffer = array(categories)

    sums = [0] * n_features
    for row in attributes:
        for i in xrange(n_features):
            if row[i] is not None:
                sums[i] += row[i]

    averages = [x / float(n_rows) for x in sums]

    for j in xrange(n_rows):
        for i in xrange(n_features):
            if attributes[j][i] is None:
                attributes[j][i] = averages[i]
        attribute_buffer[j] = attributes[j]

    return attribute_buffer, categories_buffer


class Sample:
    """
    Represents data sample. Contains methods for data preprocessing.
    """
    _fix_methods = {
        "remove": _fix_missing_remove,
        "average": _fix_missing_average
    }

    supported_fix_methods = _fix_methods.keys()

    @staticmethod
    def from_file(tabular_file, missing='remove'):
        """
        Creates a Sample object by reading contents of the specified file.
        :param filepath: Path to the file.
        :param missing: Method of handling missing values in the file.
        :return: A Sample object.
        """
        if not missing in Sample.supported_fix_methods:
            raise SampleException('Incorrect "missing" argument.')

        attributes, columns, categories = _read_tabular_data(tabular_file)

        # Check for duplicate headers
        if len(columns) != len(set(columns)):
            raise SampleException('Data file contains duplicate column headers.')

        s = Sample()
        s.columns = columns
        s.attributes, s.categories = Sample._fix_methods[missing](attributes, categories)
        s.nrows, s.ncols = s.attributes.shape

        return s

    def __init__(self):
        self.attributes = array([])
        self.columns = []
        self.categories = array([])
        self.nrows = 0
        self.ncols = 0

    def remove_column(self, column_name):
        """
        Removes an attribute column from the Sample.
        :param column_name: The name of the column which should be removed.
        """
        index = self._column_index(column_name)
        self.attributes = hstack((self.attributes[:, :index], self.attributes[:, index + 1:]))
        self.columns.remove(column_name)
        self.ncols -= 1

    def normalize_column(self, column_name, normalize_range=(0.0, 1.0)):
        """
        Scales the attribute column's values to match the specified range.
        :param column_name: The name of the column to be normalized.
        :param normalize_range: The range of normalization.
        """
        index = self._column_index(column_name)
        scale_min, scale_max = normalize_range
        maximum = max(self.attributes[:, index])
        minimum = min(self.attributes[:, index])
        self.attributes[:, index] = [scale_min + (x - minimum) / (maximum - minimum) * (scale_max - scale_min)
                                     for x in self.attributes[:, index]]

    def merge_columns(self, column_names, clusterer, new_column_name=None):
        """
        Transforms a group of columns into a new column by applying a clustering algorithm to their rows.
        :param column_names: A list of column names to be transformed.
        :param clusterer: Object implementing AbstractClusterer interface.
        :param new_column_name: The name of the produced column. If not specified, the name will be auto-generated.
        """
        if len(column_names) == 0:
            raise SampleException('List of column names can\'t be empty.')

        try:
            column_indices = [self.columns.index(c) for c in column_names]
        except:
            raise SampleException("Specified column names don't belong to sample's columns: [%s], [%s]" % (
                ", ".join(column_names), ", ".join(self.columns)))

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
        self.ncols = len(self.columns)

    def split(self, random=None, test_ratio=0.2):
        """
        Splits the sample into two subsets - evaluation sample and test sample.
        :param random: RandomState object used for selecting the split. State will not be 
        modified b the method.
        :param split_ratio: What part of the original sample will go to the test subset.
        """
        if test_ratio <= 0.0 or test_ratio >= 1.0:
            raise Exception('Test ratio must be in range (0.0, 1.0)')

        r = RandomState()
        if random:
            r.set_state(random.get_state())

        indices0 = array([i for i in xrange(self.nrows) if not self.categories[i]])
        indices1 = array([i for i in xrange(self.nrows) if self.categories[i]])

        eval0, test0 = iter(ShuffleSplit(len(indices0), n_iter=1, test_size=test_ratio, 
                                          random_state=r)).next()
        eval1, test1 = iter(ShuffleSplit(len(indices1), n_iter=1, test_size=test_ratio, 
                                          random_state=r)).next()

        eval_indices = concatenate((indices0[eval0], indices1[eval1]))
        test_indices = concatenate((indices0[test0], indices1[test1]))
        r.shuffle(eval_indices)
        r.shuffle(test_indices)

        eval_sample = self._build_sample(self.attributes[eval_indices], 
                                         self.categories[eval_indices], list(self.columns))
        test_sample = self._build_sample(self.attributes[test_indices], 
                                         self.categories[test_indices], list(self.columns))
        return eval_sample, test_sample

    @staticmethod
    def _build_sample(attributes, categories, columns):
        sample = Sample()
        sample.attributes = attributes
        sample.categories = categories
        sample.columns = columns
        sample.ncols = len(columns)
        sample.nrows = len(attributes)
        return sample

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