__author__ = 'tolkjen'

from numpy import empty, float64, array, hstack, concatenate, NaN
from numpy.random import RandomState

from xlsfile import XlsFile
from models import Normalizer
from sklearn.cross_validation import ShuffleSplit

class SampleException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)
        self.message = message

    def __str__(self):
        return self.message


def _transform_string_number(x):
    if x is None or x == "":
        return NaN
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
    :returns: A tuple of (attributes, column names, categories).
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


class Sample:
    """
    Represents data sample. Contains methods for data preprocessing.
    """

    @staticmethod
    def from_file(tabular_file, row_indices=None):
        """
        Creates a Sample object by reading contents of the specified file.
        :param filepath: Path to the file.
        :returns: A Sample object.
        """
        attributes, columns, categories = _read_tabular_data(tabular_file)

        # Check for duplicate headers
        if len(columns) != len(set(columns)):
            raise SampleException('Data file contains duplicate column headers.')

        s = Sample()
        s.columns = columns
        s.attributes, s.categories = array(attributes), array(categories)
        if row_indices:
            s.attributes, s.categories = s.attributes[row_indices], s.categories[row_indices]
        s.nrows, s.ncols = s.attributes.shape

        return s

    def __init__(self):
        self.attributes = array([])
        self.columns = []
        self.categories = array([])
        self.nrows = 0
        self.ncols = 0

    def impute_nan(self, model):
        self.attributes = model.transform(self.attributes)

    def remove_column(self, column_name):
        """
        Removes an attribute column from the Sample.
        :param column_name: The name of the column which should be removed.
        """
        index = self.column_index(column_name)
        self.attributes = hstack((self.attributes[:, :index], self.attributes[:, index + 1:]))
        self.columns.remove(column_name)
        self.ncols -= 1

    def remove_columns(self, column_names):
        for col in column_names:
            self.remove_column(col)

    def get_normalizer(self, target=(-1.0, 1.0)):
        n = Normalizer(target)
        n.fit(self)
        return n

    def normalize(self, normalizer, columns):
        for col in columns:
            if not col in self.columns:
                raise SampleException("Unknown column: " + col)
        self.attributes = normalizer.transform(self, columns)

    def merge(self, clusterer):
        clusterer.transform(self)

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
            merged = clusterer.predict(self.attributes[:, column_indices]).reshape(self.nrows, 1)
        except Exception, e:
            raise SampleException('Can\'t merge columns: {0}'.format(e))

        self.attributes = hstack((remaining, merged))
        self.columns = remaining_column_names + [new_column_name]
        self.ncols = len(self.columns)

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

    def column_index(self, column_name):
        try:
            return self.columns.index(column_name)
        except:
            raise SampleException("Sample doesn't contain data column '{0}'.".format(column_name))