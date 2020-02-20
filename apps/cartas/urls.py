#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.urls import path
from .views import Indice, RegistroCreateView, PensionadoListView, PensionadoDetailView, LeerReporteView

app_name = 'cartas'
urlpatterns = [
    path('pensionado/<int:pk>/', PensionadoDetailView.as_view(), name='pensionado_detalle'),
    path('nuevo-registro/<int:pk>', RegistroCreateView.as_view(), name='nuevo_registro'),
    path('pensionados-listado/', PensionadoListView.as_view(), name="pensionados_list"),
    path('leer-reporte/', LeerReporteView.as_view(), name="leer_reporte"),
    path('', Indice.as_view(), name='indice'),
]