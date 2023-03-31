from django.urls import path
from . import views

urlpatterns = [
    path('', views.CheckNDFLView.as_view(), name='check_ndfl'),
]