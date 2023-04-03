from io import BytesIO
from zipfile import BadZipFile

from django.http import FileResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from .services import read_income_excel, generate_outcome_excel


class CheckNDFLView(TemplateView):
    template = 'ndfl_inspector/check_ndfl.html'

    def get(self, request):
        return render(request, self.template, {'error': None})

    def post(self, request):
        income_excel = request.FILES.get('income_excel')

        try:
            first_data_row_num = int(request.POST.get('first_data_row'))
            column_nums = {
                'branch_column_num': int(request.POST.get('branch_column')),
                'employee_column_num': int(request.POST.get('employee_column')),
                'tax_base_column_num': int(request.POST.get('tax_base_column')),
                'custom_total_column_num': int(request.POST.get('custom_total_column')),
            }
        except ValueError:
            error_text = 'Ошибка, укажите верные настройки'
            return render(request, self.template, {'error': error_text}) 

        try:
            income_ndfl_table = read_income_excel(income_excel,
                                                  first_data_row_num,
                                                  column_nums)
        except BadZipFile:
            error_text = 'Ошибка загрузки файла, возможно файл неверного формата'
            return render(request, self.template, {'error': error_text})
        except IndexError:
            error_text = 'Ошибка, укажите верные настройки'
            return render(request, self.template, {'error': error_text})
        
        outcome_excel = generate_outcome_excel(income_ndfl_table)

        outcome_bytes = BytesIO()
        outcome_excel.save(outcome_bytes)
        outcome_bytes.seek(0)
        return FileResponse(outcome_bytes,
                            as_attachment=True,
                            filename='outcome.xlsx')
