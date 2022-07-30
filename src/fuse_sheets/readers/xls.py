from copy import copy
from typing import Tuple, Generator, Any, Union, Awaitable

import xlrd
from xlrd.sheet import Cell

from fuse_sheets.readers.abc import ISheetReader
from fuse_core.core.containers import FuseDictionary
from fuse_core.core.exceptions import ValueValidationError


class XlsSheetReader(ISheetReader):

    def read_file(self, content: Union[str, bytes]) -> Any:
        """
        Read file and, for example, return `openpyxl.Workbook`
        """
        return xlrd.open_workbook(filename=content)

    def get_max_row(self, workbook) -> int:
        return workbook.nrows

    def find_sheet(
        self,
        sheet_data: bytes,
        verbose_names: Tuple[str, ...]
    ) -> Any:
        for sheet in sheet_data:
            if sheet:
                if tuple(i.value for i in sheet[0]) == verbose_names:
                    return sheet

    def get_fuse_dictionary(
        self,
        sheet_data: Any,
        headers: Tuple["Field", ...]
    ) -> Union[Awaitable[Generator], Generator]:
        """
        Convert any data to `FuseDictionary` and yield it
        """
        fuse_dict = FuseDictionary()

        try:
            for ci in range(self.get_max_row(sheet_data)):
                for ri, row in enumerate(sheet_data.row_slice(ci + 1, end_colx=len(headers))):
                    field_inst = copy(headers[ri])
                    fuse_dict[field_inst.name] = field_inst
                    try:
                        if isinstance(row, Cell):
                            field_inst.validate(row.value)
                            field_inst.set(row.value)

                    except ValueValidationError:
                        self._logger.warning(f'Can\'t validate value {row.value}')

                    except Exception:
                        self._logger.warning('Something went wrong')

                    del row

                yield fuse_dict
        except IndexError:
            pass
