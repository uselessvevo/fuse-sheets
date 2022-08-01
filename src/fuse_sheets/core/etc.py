from datetime import datetime


__all__ = (
    'EXCEL_START_DATE', 'STYLE_14_VALUES',
    'STYLE_22_VALUES', 'STYLE_14', 'STYLE_18', 'STYLE_22',
    'CELL_TYPE_STRING', 'CELL_TYPE_DIGIT', 'CELL_TYPE_BOOLEAN',
    'CELL_TYPE_EMPTY', 'CELL_TYPE_DATE', 'CELL_TYPE_TIME',
)


EXCEL_START_DATE = datetime(1899, 12, 30)

# Style values to get styles

STYLE_14_VALUES = (r'm/d/yy\ h:mm',)
STYLE_18_VALUES = ('mm:ss', 'h:mm')
STYLE_22_VALUES = (
    r'dddd\,\ mmmm\ dd\,\ yyyy', 'm/d', r'yyyy\-mm\-dd',
    'mm/dd/yy', r'd\-mmm', r'mmm\-yy', r'mmmm\ d\,\ yyyy', 'mmmmm', r'd\-mmm\-yyyy'
)

# Magic numbers for parsing

STYLE_14 = '14'
STYLE_18 = '18'
STYLE_22 = '22'

# Cell types for parsing

CELL_TYPE_STRING = 's'
CELL_TYPE_DIGIT = 'n'
CELL_TYPE_BOOLEAN = 'b'
CELL_TYPE_EMPTY = ('', 'str', 'e')
CELL_TYPE_DATE = ('14', '15', '16', '17')
CELL_TYPE_TIME = ('18', '19', '20', '21')
