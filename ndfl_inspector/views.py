from django.http import FileResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from .services import read_income_excel, generate_outcome_excel

class CheckNDFLView(TemplateView):
    template = 'ndfl_inspector/check_ndfl.html'

    def get(self, request):
        return render(request, self.template)
    
    def post(self, request):
        ndfl_file = request.FILES.get('ndfl_table')
        income_ndfl_table = read_income_excel(ndfl_file, 3)
        outcome_excel = generate_outcome_excel(income_ndfl_table)
        return FileResponse(outcome_excel, as_attachment=True, filename='outcome.xlsx')
        

