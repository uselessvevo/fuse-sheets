import asyncio
from fuse_core.handlers.fields import Field
from fuse_sheets.tasks import FuseSheetsTask
from fuse_sheets.readers import XlsxSheetReader


headers = (
    Field(
        name='firstname',
        verbose_name='Имя'
    ),
    Field(
        name='surname',
        verbose_name='Фамилия'
    ),
    Field(
        name='lastname',
        verbose_name='Отчество'
    ),
    Field(
        name='age',
        verbose_name='Возраст'
    ),
    Field(
        name='address',
        verbose_name='Адрес',
    )
)


async def main():
    task = FuseSheetsTask(headers)
    await task.prepare('../test.xlsx')
    await task.handle()
    # await asyncio.gather(
    #     *[task.handle() for _ in range(100)],
    # )
    # await asyncio.gather(
    #     task.handle(),
    #     task.handle(),
    #     task.handle(),
    #     task.handle(),
    #     task.handle(),
    #     task.handle(),
    # )


asyncio.run(main())
