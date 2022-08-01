from __future__ import annotations

from collections import OrderedDict

from fuse_sheets.web.enums import SheetsLoggerEnum


class BaseSheetsLogger:
    """
    Logger that saves logs into json and database
    """

    def __init__(self, parent_logger=None):
        self._logs = []
        self._logger = parent_logger

    async def info(self, *keys, items: object = None, comment: str = None):
        await self.record(*keys, comment=comment, items=items, state=SheetsLoggerEnum.INFO)

    async def error(self, *keys, item: object = None, comment: str = None):
        await self.record(*keys, comment=comment, items=item, state=SheetsLoggerEnum.ERROR)

    async def warning(self, *keys, items: object = None, comment: str = None):
        await self.record(*keys, comment=comment, items=items, state=SheetsLoggerEnum.WARNING)

    async def record(
        self,
        *keys,
        items: "FuseDictionary" = None,
        comment: str = None,
        state: SheetsLoggerEnum = SheetsLoggerEnum.ERROR
    ) -> None:
        container = OrderedDict({
            k: {
                'value': items.get(k),
                'broken': False,
                'comment': None,
                'state': SheetsLoggerEnum.INFO.value,
                'verbose_name': items.field(k, attr='verbose_name'),
            } for (k, v) in items.get_items().items()
        })

        for k in keys:
            container[k].update({
                'value': items.get(k),
                'comment': comment,
                'state': state.value,
                'verbose_name': items.field(k, attr='verbose_name')
            })
            self._logger.warning(comment)

        self._logs.append(container)

    async def save(self, **kwargs) -> None:
        raise NotImplementedError('method `save` must be implemented')
