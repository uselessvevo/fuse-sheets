import re
import zipfile
import warnings
from pathlib import Path
from typing import Tuple
from datetime import timedelta
from xml.etree import cElementTree as ET

from fuse_core.core.utils import get_separator

from fuse_core.core.fields import *
from fuse_sheets.core.etc import *

from fuse_sheets.core.utils import get_xml_namespace
from fuse_sheets.core.worksheet import Worksheet


class Workbook:

    def __init__(
        self,
        filename: str,
        fields: Tuple[Field] = None,
        worksheets: Tuple[str] = None,
    ) -> None:
        """
        Args:
            filename (str): path to excel file
            worksheets (Tuple[str]): list of expected sheet names
        """
        self._filename = Path(filename)
        self._fields = fields
        self._worksheets = worksheets
        if not self._filename.exists():
            raise FileNotFoundError

    def read(self):
        raw_workbook = self.read_excel_file()
        if not raw_workbook.get('worksheet') and raw_workbook.get('namespace'):
            raise ValueError('Raw data is empty')

        self.prepare_worksheets(raw_workbook)

    def read_excel_file(self) -> dict:
        result = {'worksheet': {}, 'namespace': {}}

        with zipfile.ZipFile(self._filename, 'r') as f_zip:
            # reading inner xml files
            with f_zip.open('xl/workbook.xml', 'r') as wb_file:
                namespace = get_xml_namespace(wb_file)
                for prefix, uri in namespace.items():
                    ET.register_namespace(prefix, uri)

            with f_zip.open('xl/workbook.xml', 'r') as wb_file:
                tree = ET.parse(wb_file)
                root = tree.getroot()

        wb_relations = self.get_workbook_relations()
        for tag_sheet in root.findall('./default:sheets/default:sheet', namespace):
            name = tag_sheet.get('name')
            try:
                r_id = tag_sheet.get('{%s}id' % namespace['r'])
            except KeyError:
                r_id = tag_sheet.get('id')

            sheet_id = int(re.sub(r'[^0-9]', '', r_id))
            result['worksheet'][name] = {
                'worksheet': name,
                'r_id': r_id,
                'order': sheet_id,
                'workbook_filename': wb_relations[r_id]
            }

        for tag_sheet in root.findall('./default:definedNames/default:definedName', namespace):
            name = tag_sheet.get('name')
            # For user friendly entry, the "$" for locked cell-locations are removed
            full_address = tag_sheet.text.replace('$', '')
            try:
                ws, address = full_address.split('!')
            except ValueError:
                msg = ('fuse-lightxl - Ill formatted "workbook.xml". '
                       'Skipping "NamedRange" not containing sheet reference (ex: "Sheet1!A1"): '
                       '{name} - {full_address}'.format(name=name, full_address=full_address))
                warnings.warn(msg, UserWarning)
                continue

            result['namespace'][name] = {'namespace': name, 'worksheet': ws, 'address': address}

        return result

    def prepare_worksheets(self, workbook: dict):
        worksheets = self._worksheets or self.get_worksheet_by_map()
        for worksheet in worksheets:
            self.read_sheets_data(
                ws_filename=workbook[worksheet]['worksheet'],
            )

    def get_shared_strings(self):
        """
        Takes a file-path for xl/sharedStrings.xml
        and returns a dictionary of commonly used strings
        """
        shared_strings = {}

        # zip up the excel file to expose the xml files
        with zipfile.ZipFile(self._filename, 'r') as f_zip:

            if 'xl/sharedStrings.xml' not in f_zip.NameToInfo.keys():
                return shared_strings

            with f_zip.open('xl/sharedStrings.xml', 'r') as file:
                ns = get_xml_namespace(file)
                for prefix, uri in ns.items():
                    ET.register_namespace(prefix, uri)

            with f_zip.open('xl/sharedStrings.xml', 'r') as file:
                tree = ET.parse(file)
                root = tree.getroot()

        for index, tag_si in enumerate(root.findall('./default:si', ns)):
            tag_t = tag_si.findall('./default:r//default:t', ns)
            if tag_t:
                text = ''.join([tag.text for tag in tag_t if tag.text])
            else:
                text = tag_si.findall('./default:t', ns)[0].text
            shared_strings.update({index: text})

        return shared_strings

    def get_styles(self):
        """
        Takes a file-path for xl/styles.xml
        and returns a dictionary of commonly used strings
        """
        styles = {0: '0'}

        # zip up the excel file to expose the xml files
        with zipfile.ZipFile(self._filename, 'r') as f_zip:
            if 'xl/styles.xml' not in f_zip.NameToInfo.keys():
                return styles

            with f_zip.open('xl/styles.xml', 'r') as file:
                ns = get_xml_namespace(file)
                for prefix, uri in ns.items():
                    ET.register_namespace(prefix, uri)

            with f_zip.open('xl/styles.xml', 'r') as file:
                tree = ET.parse(file)
                root = tree.getroot()

        custom_styles = {}
        try:
            tag_num_fmts = root.findall('./default:numFmts', ns)[0]
        except IndexError:
            tag_num_fmts = []

        for tag in tag_num_fmts:
            if any((time_type in tag.get('formatCode') for time_type in STYLE_22_VALUES)):
                custom_styles[tag.get('numFmtId')] = STYLE_22
            elif any((datetype in tag.get('formatCode') for datetype in STYLE_14_VALUES)):
                custom_styles[tag.get('numFmtId')] = STYLE_14

            elif any((time_type in tag.get('formatCode') for time_type in STYLE_14_VALUES)):
                custom_styles[tag.get('numFmtId')] = STYLE_18

        for index, tag_cell_xfs in enumerate(root.findall('./default:cellXfs', ns)[0]):
            num_fmt_id = tag_cell_xfs.get('numFmtId')
            styles.update({index: custom_styles[num_fmt_id] if num_fmt_id in custom_styles else num_fmt_id})

        return styles

    def read_sheets_data(self, ws_filename: str) -> Worksheet:
        worksheet = Worksheet()
        shared_strings = self.get_shared_strings()
        styles = self.get_styles()

        # zip up the excel file to expose the xml files
        with zipfile.ZipFile(self._filename, 'r') as f_zip:
            with f_zip.open(f'xl/worksheets/{ws_filename.lower()}.xml', 'r') as file:
                namespace = get_xml_namespace(file)
                for prefix, uri in namespace.items():
                    ET.register_namespace(prefix, uri)

            with f_zip.open(f'xl/worksheets/{ws_filename.lower()}.xml', 'r') as file:
                tree = ET.parse(file)
                root = tree.getroot()

        for tag_cell in root.findall('./default:sheetData/default:row/default:c', namespace):
            """
            Note:
                t="e" is for error cells "#N/A"
                t="s" is for common strings
                t="str" is for equation strings (ex: =A1 & "this")
                t="b" is for bool, bool is not logged as a commonString in xml, 0 == FALSE, 1 == TRUE
            """
            tag_formula = tag_cell.find('./default:f', namespace)
            cell_address = tag_cell.get('r')
            cell_type = tag_cell.get('t')
            cell_style = int(tag_cell.get('s')) if tag_cell.get('s') is not None else 0
            tag_val = tag_cell.find('./default:v', namespace)
            cell_value = tag_val.text or '' if tag_val is not None else ''

            # Parsing

            if cell_type == CELL_TYPE_STRING:
                # Common string
                cell_value = shared_strings.get(int(cell_value))
                field = StringField()
                field.set(cell_value)

            elif cell_type == CELL_TYPE_DIGIT:
                separator = get_separator(['.', ','], cell_value)
                if separator:
                    cell_value = float(cell_value.replace(separator, '.'))
                    field = FloatField()
                    field.set(cell_value)
                    print(f'{field=}')
                else:
                    cell_value = int(cell_value)
                    field = IntegerField()
                    field.set(cell_value)
                    print(f'{field=}')

            elif cell_type == CELL_TYPE_BOOLEAN:
                # Boolean string
                cell_value = True if cell_value == '1' else False
                field = Field()
                field.set(cell_value)
                print(f'{field=}')

            elif cell_type in CELL_TYPE_EMPTY:
                # Empty cell or cell with formula
                field = StringField()
                field.set('')

            else:
                # Integer, float value and other numeric values
                digit_cell = cell_value if '-' not in cell_value else cell_value[1:]
                if digit_cell.isdigit():
                    cell_style_value = styles.get(cell_style)
                    partial_day = float(cell_value) % 1

                    if cell_style_value in CELL_TYPE_DATE:
                        cell_value = (EXCEL_START_DATE + timedelta(days=int(cell_value))).strftime('%Y/%m/%d')
                        field = Field()
                        field.set(cell_value)
                        print(f'{field=}')

                    elif cell_style_value in CELL_TYPE_TIME:
                        cell_value = (EXCEL_START_DATE + timedelta(seconds=partial_day * 86400)).strftime('%H:%M:%S')
                        field = Field()
                        field.set(cell_value)
                        print(f'{field=}')

                    elif cell_style_value == STYLE_22:
                        pd_first = (EXCEL_START_DATE + timedelta(days=int(cell_value.split('.')[0]))).isoformat()
                        pd_first = pd_first.split('T')[0]

                        pd_second = (EXCEL_START_DATE + timedelta(seconds=partial_day * 86400)).isoformat()
                        pd_second = pd_second.split('T')[1]

                        cell_value = f"{pd_first} {pd_second}"
                        cell_value = '/'.join(cell_value)

                        field = Field()
                        field.set(cell_value)
                        print(f'{field=}')

        return worksheet

    def get_workbook_relations(self) -> dict:
        collect = {}

        # Zip up the excel file to expose the xml files
        with zipfile.ZipFile(str(self._filename), 'r') as f_zip:
            with f_zip.open('xl/_rels/workbook.xml.rels', 'r') as file:
                ns = get_xml_namespace(file)
                for prefix, uri in ns.items():
                    ET.register_namespace(prefix, uri)

            with f_zip.open('xl/_rels/workbook.xml.rels', 'r') as file:
                tree = ET.parse(file)
                root = tree.getroot()

            for relationship in root.findall('./default:Relationship', ns):
                filename_worksheet = relationship.get('Target')
                # Openpyxl write its xl/_rels/workbook.xml.rels file differently than excel itself.
                # It adds on /xl/ at the start of the file path
                if filename_worksheet[:4] == '/xl/':
                    filename_worksheet = filename_worksheet[4:]

                r_id = relationship.get('Id')
                collect[r_id] = filename_worksheet

            return collect
