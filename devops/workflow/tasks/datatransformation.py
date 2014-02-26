"""
The datatransformation module offers classes that transform data in some way.

The XlsToCsv class takes an Excel (xls) file and converts it to csv format.
"""

import csv
import xlrd
from ..workflow import DevOpsTask


class XlsToCsv(DevOpsTask):

    """
    XlsToCsv class takes an Excel (xls) file and converts it to csv format.
    """

    def __init__(self, source, destination):

        """
        self.source => The source xls file to convert.
        self.destination = The target (output) csv file.
        """

        super().__init__()
        self.source = source
        self.destination = destination

    def execute(self, step_name=''):

        """
        At the moment, the csv writer spits out a "csv" file using a | as a delimiter. This is because it is used in an example; this will
        be changed to use a config entry in the next version.
        """

        super().execute(step_name)
        book = xlrd.open_workbook(self.source)
        sheet = book.sheets()[0]
        with open(self.destination, 'w') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_NONE)
            for rowNum in range(sheet.nrows):
                csvwriter.writerow(sheet.row_values(rowNum))
        self._w_print('A copy of the xls file {} has been saved using csv format. Saved to: {}'.format(self.source, self.destination))