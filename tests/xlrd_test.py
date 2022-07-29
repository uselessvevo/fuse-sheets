import xlrd


workbook = xlrd.open_workbook('test.xls')
sheet = workbook.sheet_by_name('Sheet1')


for index, column in enumerate(sheet, start=2):
    print(index, column)
