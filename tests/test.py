import asyncio

from fuse_core.orm.validators import EmailValidator

from src.fuse_sheets.tasks import FuseSheetsTask
from fuse_core.core.fields import Field, IntegerField


headers = (
    Field(
        name='firstname',
        verbose_name='Firstname'
    ),
    Field(
        name='surname',
        verbose_name='Surname'
    ),
    Field(
        name='patronymic',
        verbose_name='Patronymic'
    ),
    IntegerField(
        name='age',
        verbose_name='Age'
    ),
    Field(
        name='address',
        verbose_name='Address',
    ),
    Field(
        name='email',
        verbose_name='Email',
        validators=[EmailValidator()]
    ),
    Field(
        name='date_of_birth',
        verbose_name='Date of birth'
    )
)


async def single_main():
    task = FuseSheetsTask(headers)
    await task.prepare('test.xls')
    await task.handle()


async def hundred_runs():
    task = FuseSheetsTask(headers)
    await task.prepare('test.xlsx')
    await asyncio.gather(
        *[task.handle() for _ in range(100)],
    )


async def gather_runs():
    task = FuseSheetsTask(headers)
    await task.prepare('test.xlsx')
    await asyncio.gather(
        task.handle(),
        task.handle(),
        task.handle(),
        task.handle(),
        task.handle(),
        task.handle(),
    )


asyncio.run(single_main())
