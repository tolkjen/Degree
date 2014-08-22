# coding=utf-8
import xlrd


class XlsFile:
    def __init__(self, filepath):
        """
        Creates an object representing contents of XLS file.
        :param filepath: Path to the XLS file.
        """
        self._column_names = []
        self._row_list = []
        self._workbook = None

        try:
            self._workbook = xlrd.open_workbook(filepath)
        except:
            raise Exception('Nie można otworzyć pliku lub nieprawidłowy rodzaj pliku.')

    def read(self):
        """
        Attempts to open a file an read all of its contents (data rows).
        """
        if self._workbook is None:
            raise Exception('Nie można odczytać pliku lub nieprawidłowy rodzaj pliku.')

        datasheet = None
        worksheets = self._workbook.sheets()
        for worksheet in worksheets:
            if worksheet.ncols > 0:
                datasheet = worksheet
                break

        if datasheet is None:
            raise Exception('Plik nie zawiera żadnych danych.')

        header_column_indices = []
        header_row = datasheet.row(0)
        for (index, cell) in enumerate(header_row):
            if cell.ctype == 1:
                header_column_indices.append(index)
                self._column_names.append(str(cell.value))

        if not header_column_indices:
            raise Exception('Plik nie zawiera wiersza z nazwami kolumn.')

        row_index = 1
        while row_index < datasheet.nrows:
            row = []
            for col_index in header_column_indices:
                row.append(str(datasheet.cell(row_index, col_index).value))
            self._row_list.append(row)
            row_index += 1

    def columns(self):
        """
        Returns a list of column names.
        :return: A list of column names.
        """
        return self._column_names

    def rows(self):
        """
        Returns a list of entry rows from the file. Each entry row is a string list.
        :return: A list of entry rows.
        """
        return self._row_list
