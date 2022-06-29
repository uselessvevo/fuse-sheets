from __future__ import annotations

import abc
import dataclasses as dt
from typing import Tuple, Union, Generator, Awaitable, Any


@dt.dataclass
class SheetWorkbook:
    """
    Sheet workbook contains data about sheet file
    Works like a bridge pattern structure
    """

    file_name: str
    min_row: int
    max_row: int
    min_col: int
    max_col: int


class ISheetReader:

    @staticmethod
    @abc.abstractmethod
    def read_file(content: Union[str, bytes]) -> bytes:
        """
        Read file and convert output
        data to tuple filled with `SheetItem` structs
        """

    @staticmethod
    @abc.abstractmethod
    def find_sheet(sheet_data: bytes, verbose_names: Tuple[str, ...]) -> SheetWorkbook:
        """
        Find needed sheet and convert data to `SheetWorkbook`
        """

    @staticmethod
    @abc.abstractmethod
    def get_fuse_dictionary(sheet_data: Any, headers: Tuple["Field", ...]) -> Union[Awaitable[Generator, ...], Generator]:
        """
        Convert `Tuple[SheetItem, ...]` to `FuseDictionary`
        """
