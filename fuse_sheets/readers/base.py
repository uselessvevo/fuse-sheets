from __future__ import annotations

import abc
from typing import Tuple, Union, Generator, Awaitable, Any


class ISheetReader:

    @staticmethod
    @abc.abstractmethod
    def read_file(content: Union[str, bytes]) -> Any:
        """
        Read file and, for example, return `openpyxl.Workbook`
        """

    @staticmethod
    @abc.abstractmethod
    def find_sheet(sheet_data: bytes, verbose_names: Tuple[str, ...]) -> Any:
        """
        Find needed sheet
        """

    @staticmethod
    @abc.abstractmethod
    def get_fuse_dictionary(
        sheet_data: Any,
        headers: Tuple["Field", ...]
    ) -> Union[Awaitable[Generator, ...], Generator]:
        """
        Convert any data to `FuseDictionary` and yield it
        """
