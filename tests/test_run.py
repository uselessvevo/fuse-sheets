import pytest
from fuse_core.core.containers import FieldDictionary
from fuse_sheets.web.tasks import FuseSheetsTask
from tests.base import HEADERS, SimpleSheetLogger


@pytest.mark.asyncio
async def test_task():
    class TestFuseTask(FuseSheetsTask):
        sheets_logger = SimpleSheetLogger

        async def item_handler(self, item: FieldDictionary) -> None:
            self.logger.info(item.get_values(full_house=True))

    task = TestFuseTask(headers=HEADERS)
    await task.prepare('test.xls')
    await task.handle()
