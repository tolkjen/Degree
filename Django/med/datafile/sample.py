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

		class_column_index = 0
		try:
			class_column_index = [s.lower() for s in datafile.columns()].index('index')
		except:
			raise Exception('Plik nie posiada kolumny o nazwie "Index".')

		sample = Sample()
		sample.column_count = len(datafile.columns())
		for row in datafile.rows():
			attributes = row[:class_column_index] + row[class_column_index+1:]
			sample.data_rows.append( (attributes, row[class_column_index]) )

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
		self.column_count = 0

	def rows(self):
		return self.data_rows

	def transform_attributes(self, str_trans, num_trans):
		column_numeric = [True] * self.column_count
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

if __name__ == "__main__":
	sample = Sample.fromFile('data.xls')
	sample.transform_attributes(StringTransform(), RangeNumberTransform(5))
	for row in sample.rows():
		print row
