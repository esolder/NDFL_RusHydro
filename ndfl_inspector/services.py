from collections import namedtuple
from io import BytesIO

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet


TAX_THRESHOLD = 5000000
PERCENT_BEFORE_THRESHOLD = 0.13
PERCENT_AFTER_THRESHOLD = 0.15
A_LETTER_NUMBER = ord('A')


def read_income_excel(filepath: str, start_row: int) -> list:
    income_file = openpyxl.load_workbook(filepath, read_only=True)
    income_sheet = income_file.active
    columns = (
        'branch',
        'employee',
        'income',
        'tax',
        'ndfl_base',
        'custom_calculation',
        'withheld_tax',
    )
    EmployeeNDFL = namedtuple('EmployeeNDFL', columns)

    income_ndfl_table = []
    for row in income_sheet.iter_rows(values_only=True, min_row=start_row):
        ndfl_row = EmployeeNDFL(*row)
        if ndfl_row.employee:
            income_ndfl_table.append(ndfl_row)

    income_file.close()
    return income_ndfl_table


def generate_outcome_excel(income_ndfl_table: list) -> BytesIO:
    outcome_file = openpyxl.Workbook()
    outcome_sheet = outcome_file.active
    for row_number, row in enumerate(income_ndfl_table, 1):
        calculation = _calculate_ndfl(row.ndfl_base)

        deviation = _calculate_deviation(row.custom_calculation, calculation)

        result_row = (
            row.branch,
            row.employee,
            row.ndfl_base,
            row.custom_calculation,
            calculation,
            deviation,
        )
        outcome_sheet.append(result_row)


    _generate_outcome_header(outcome_sheet)

    outcome_bytes = BytesIO()

    outcome_file.save(outcome_bytes)

    outcome_bytes.seek(0)

    return outcome_bytes


def _calculate_ndfl(ndfl_base: float) -> int:
    if not ndfl_base:
        return 0
    if ndfl_base < TAX_THRESHOLD:
        return round(ndfl_base * PERCENT_BEFORE_THRESHOLD)
    return round(ndfl_base * PERCENT_AFTER_THRESHOLD)


def _calculate_deviation(custom_calc: int | None, calc: int) -> int:
    return custom_calc - calc if custom_calc else -calc


def _generate_outcome_header(sheet: Worksheet) -> None:
    sheet.insert_rows(1, 2)

    sheet.merge_cells('A1:A2')
    sheet['A1'] = 'Филиал'

    sheet.merge_cells('B1:B2')
    sheet['B1'] = 'Сотрудник'

    sheet.merge_cells('C1:C2')
    sheet['C1'] = 'Налоговая база'

    sheet.merge_cells('D1:E1')
    sheet['D1'] = 'Налог'

    sheet['D2'] = 'Исчислено всего'
    sheet['E2'] = 'Исчислено всего по формуле'

    sheet.merge_cells('F1:F2')
    sheet['F1'] = 'Отклонения'
