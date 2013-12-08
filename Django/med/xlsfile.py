import xlrd

class XlsFile:
	column_names = []
	row_list = []

	def __init__(self, filepath):
		workbook = xlrd.open_workbook(filepath)

		datasheet = None
		worksheets = workbook.sheets()
		for worksheet in worksheets:
			if worksheet.ncols > 0:
				datasheet = worksheet
				break

		if datasheet == None:
			raise Exception('Workbook doesn\'t contain any data.')

		header_column_indices = []
		header_row = datasheet.row(0)
		for (index, cell) in enumerate(header_row):
			if cell.ctype == 1:
				header_column_indices.append(index)
				self.column_names.append(str(cell.value))

		if (header_column_indices == []):
			raise Exception('Workbook doesn\'t contain column header')

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

if __name__ == "__main__":
	reader = XlsFile("data.xls")
	print reader.columns()
