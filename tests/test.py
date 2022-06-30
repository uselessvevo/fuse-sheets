import asyncio

from fuse_core.orm.validators import EmailValidator

from fuse_sheets.tasks import FuseSheetsTask
from fuse_core.handlers.fields import Field, IntegerField


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
)


async def main():
    task = FuseSheetsTask(headers)
    await task.prepare('test.xlsx')
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
