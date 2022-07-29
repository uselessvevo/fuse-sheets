from __future__ import annotations

import abc
from typing import Tuple, Union, Generator, Awaitable, Any


class ISheetReader:

    @abc.abstractmethod
    def read_file(self, content: Union[str, bytes]) -> Any:
        """
        Read file and, for example, return `openpyxl.Workbook`
        """

    @abc.abstractmethod
    def find_sheet(
        self,
        sheet_data: bytes,
        verbose_names: Tuple[str, ...]
    ) -> Any:
        """
        Find needed sheet
        """

    def get_max_row(self, workbook) -> int:
        """
        Get max row. F.e. openpyxl provides `max_row` attr
        """

    @abc.abstractmethod
    def get_fuse_dictionary(
        self,
        sheet_data: Any,
        headers: Tuple["Field", ...]
    ) -> Union[Awaitable[Generator, ...], Generator]:
        """
        Convert any data to `FuseDictionary` and yield it
        """
