class SheetsFakeError(Exception):
    """
    Pass this exception to skip `items_handler` loop
    """


class SheetsInlineError(Exception):

    __slots__ = ('_fields', '_comment')

    def __init__(self, *fields, comment: str = None) -> None:
        self._fields = fields
        self._comment = comment

    @property
    def fields(self):
        return self._fields

    @property
    def comment(self):
        return self._comment
