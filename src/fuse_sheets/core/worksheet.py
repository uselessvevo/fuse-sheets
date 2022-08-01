"""
Excel worksheet container
"""
from typing import List

from fuse_core.core.containers import FieldDictionary


class Worksheet:

    def __init__(self) -> None:
        self.__container: List[FieldDictionary] = []

        # Cols and rows
        self._maxrow = 0
        self._minrow = 0

        self._maxcol = 0
        self._mincol = 0

    @property
    def maxrow(self):
        return self._maxrow

    @property
    def minrow(self):
        return self._minrow

    @property
    def maxcol(self):
        return self._maxcol

    @property
    def mincol(self):
        return self._mincol

    def append(self, field_dict: FieldDictionary) -> None:
        if not isinstance(field_dict, FieldDictionary):
            raise TypeError('Argument `field_dict` must be an instance of `FieldDictionary`')

        self.__container.append(field_dict)

    def __getitem__(self, key):
        return self.__container[key]

    def __setitem__(self, key, field_dict):
        if not isinstance(field_dict, FieldDictionary):
            raise TypeError('Argument `field_dict` must be an instance of `FieldDictionary`')

        self.__container[key] = field_dict

    def __repr__(self) -> str:
        return f'{self.__class__.__name__} <id: {id(self)}>'
