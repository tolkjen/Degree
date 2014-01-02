# coding=utf-8

import xlrd

class XlsFile:
	def __init__(self, filepath):
		self.column_names = []
		self.row_list = []
		self.workbook = None

		try:
			self.workbook = xlrd.open_workbook(filepath)
		except:
			raise Exception('Nie można otworzyć pliku lub nieprawidłowy rodzaj pliku.')

	def read(self):
		if (self.workbook == None):
			raise Exception('Nie można odczytać pliku lub nieprawidłowy rodzaj pliku.')

		datasheet = None
		worksheets = self.workbook.sheets()
		for worksheet in worksheets:
			if worksheet.ncols > 0:
				datasheet = worksheet
				break

		if datasheet == None:
			raise Exception('Plik nie zawiera żadnych danych.')

		header_column_indices = []
		header_row = datasheet.row(0)
		for (index, cell) in enumerate(header_row):
			if cell.ctype == 1:
				header_column_indices.append(index)
				self.column_names.append(str(cell.value))

		if (header_column_indices == []):
			raise Exception('Plik nie zawiera wiersza z nazwami kolumn.')

		row_index = 1
		while row_index < datasheet.nrows:
			row = []
			for col_index in header_column_indices:
				row.append( str(datasheet.cell(row_index, col_index).value) )
			self.row_list.append(row)
			row_index = row_index + 1

	def columns(self):
		return self.column_names

	def rows(self):
		return self.row_list
		