from fuse_sheets.core.workbook import Workbook

wb = Workbook('tests/test.xlsx', ('Sheet1',))
wb.read()
