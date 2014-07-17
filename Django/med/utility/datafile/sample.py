import xlsfile
import os

from transform import RangeNumberTransform, StringTransform

class Sample:
	@staticmethod
	def fromFile(filepath):
		return Sample.fromXls(filepath)

	@staticmethod
	def fromXls(filepath):
		datafile = xlsfile.XlsFile(filepath)
		datafile.read()

		category_column_index = 0
		try:
			category_column_index = [s.lower() for s in datafile.columns()].index('index')
		except:
			raise Exception('Plik nie posiada kolumny o nazwie "Index".')

		sample = Sample()
		sample.attribute_column_count = len(datafile.columns()) - 1
		for row in datafile.rows():
			attributes = row[:category_column_index] + row[category_column_index+1:]

			attr_not_empty = reduce(lambda a, b: a and b != '', attributes, True)
			cat_not_empty = row[category_column_index] != ''

			if attr_not_empty and cat_not_empty:
				sample.data_rows.append( (attributes, row[category_column_index]) )

		return sample

	@staticmethod
	def is_numeric(x):
		try:
			float(x)
			return True
		except:
			return False

	def __init__(self):
		self.data_rows = []
		self.attribute_column_count = 0

	def rows(self):
		return self.data_rows

	def positive_count(self):
		return sum([1 for (attributes, value) in self.data_rows if value == "1.0"])

	def transform_attributes(self, str_trans, num_trans):
		column_numeric = [True] * self.attribute_column_count
		for (attributes, value) in self.data_rows:
			for (index, attribute) in enumerate(attributes):
				if column_numeric[index]:
					column_numeric[index] = Sample.is_numeric(attribute)
		
		mapper = {True: num_trans, False: str_trans}
		transformers = [mapper[is_numeric].clone() for is_numeric in column_numeric]
		for (attributes, value) in self.data_rows:
			for (index, attribute) in enumerate(attributes):
				transformers[index].put(attribute)

		new_rows = []
		for (attributes, value) in self.data_rows:
			new_attributes = [transformers[i].transform(attr) for (i, attr) in enumerate(attributes)]
			new_rows.append( (new_attributes, value) )
		self.data_rows = new_rows
