from __future__ import annotations

import logging
from aioify import aioify
from typing import Tuple, Awaitable

from fuse_core.handlers.containers import FuseDictionary

from .logger import SheetsLogger
from .readers import XLSBTableReader
from .readers import XlsxSheetReader
from .exceptions import SheetsFakeError
from .exceptions import SheetsInlineError


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
    def prepare(self, file_name: str) -> None:
        """
        Prepare file content, main attributes, `Logger` and `SheetLogger`
        """
        self.file_name = file_name
        self.file_format = file_name.split('.')[-1]

        try:
            self.reader = self.file_readers[self.file_format]()
        except KeyError:
            raise ValueError(f'can\'t handle {self.file_format} file format (file reader not found)')

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
        # temporary until we figure out how to get `max_row` from other file formats
        percent_each = 100 / workbook_sheet.max_row

        for index, item in enumerate(await self.iter_sheets(workbook_sheet)):
            try:
                await self.item_handler(item)

            except SheetsFakeError:
                pass

            except SheetsInlineError as e:
                await self.sheets_logger.error(*e.fields, item=item, comment=e.comment)

            # Set progress here
            self.logger.warning(f'{self.file_name}: {(index + 1) * round(percent_each)}% / 100%')

        # State recorder save here
        await self.sheets_logger.save(filename=self.file_name)

    async def item_handler(self, item: FuseDictionary) -> None:
        raise NotImplementedError('method `item_handler` must be implemented')
