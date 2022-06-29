from __future__ import annotations

import logging
from io import BufferedReader

from aioify import aioify
from os import path as osp
from tempfile import NamedTemporaryFile

from typing import Tuple, Awaitable, Union

from fuse_core.handlers.containers import FuseDictionary

from .logger import SheetsLogger
from .readers import XLSBTableReader
from .readers import XlsxSheetReader
from .exceptions import SheetsFakeError


class FuseSheetsTask:

    # Chunk size
    chunk_size: int = 50

    # Sleep per chunk
    sleep_per_chunk: float = .2

    # File readers mapping
    file_readers: dict = {
        'xlsx': XlsxSheetReader,
        'xlsb': XLSBTableReader,
    }

    exceptions: Tuple[Exception] = (
        ValueError,
        IndexError,
        OverflowError,
        AttributeError,
    )

    def __init__(self, headers: Tuple["Field", ...]) -> None:
        self.file_name = None
        self.file_format = None

        self.max_row: int = 1
        self.headers = headers

        # Logger
        self.logger: "Logger" = logging.getLogger(self.__class__.__name__)
        self.sheets_logger: SheetsLogger = SheetsLogger()

    @aioify
    def prepare(
        self,
        file: Union[BufferedReader, NamedTemporaryFile],
        file_name: str
    ) -> None:
        """
        Prepare file content, main attributes, `Logger` and `SheetLogger`
        """
        # Check if file is `NamedTemporaryFile`
        if getattr(file, 'getvalue'):
            file = file.getvalue()
            file_format = file_name.name.split('.')[-1]
        else:
            file_format = file.split('.')[-1]
            file_name = osp.basename(file)

        self.file_name = file_name
        self.file_format = file_format

        try:
            self.reader = self.file_readers[self.file_format]()
        except KeyError:
            raise ValueError(f'can\'t handle {self.file_format} file format')

    @aioify
    def prepare_workbook_sheet(self):
        workbook_sheet = self.reader.find_sheet(
            sheet_data=self.reader.read_file(self.file_name),
            verbose_names=tuple(i.verbose_name for i in self.headers)
        )
        return workbook_sheet

    @aioify
    def iter_sheets(self, workbook_sheet) -> Awaitable:
        yield from self.reader.get_fuse_dictionary(
            sheet_data=workbook_sheet,
            headers=self.headers
        )

    async def handle(self) -> None:
        workbook_sheet = await self.prepare_workbook_sheet()
        percent_each = 100 / workbook_sheet.max_row

        for index, item in enumerate(await self.iter_sheets(workbook_sheet)):
            try:
                await self.item_handler(item)

            except SheetsFakeError:
                pass

            except self.exceptions as e:
                # Set state here
                await self.sheets_logger.info('sexo')

            # Set progress here
            self.logger.warning(f'{self.file_name}: {(index + 1) * round(percent_each)}% / 100%')

        # State recorder save here
        # self.sheets_logger.save(user_id=self.user_id, filename=self.file_name)

    async def item_handler(self, item: FuseDictionary) -> None:
        self.logger.warning(item)
