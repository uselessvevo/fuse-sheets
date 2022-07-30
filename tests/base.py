from fuse_core.core.fields import *
from fuse_core.orm.validators import *

from fuse_sheets import BaseSheetsLogger

HEADERS = (
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


class SimpleSheetLogger(BaseSheetsLogger):

    async def save(self, **kwargs) -> None:
        self._logger.info('Saving data into database')
