from django.shortcuts import render
from django.views.generic import TemplateView

class CheckNDFLView(TemplateView):
    template_name = 'ndfl_inspector/check_ndfl.html'

    def get(self, request):
        return render(request, 'ndfl_inspector/check_ndfl.html', {})
