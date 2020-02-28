#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.urls import path
from .views import (Indice, RegistroCreateView, PensionadoListView, 
    PensionadoDetailView, LeerReporteView, PlazoListView, AltaPlazos, 
    BuscarMontoPlazoView, GenerarArchivosPensionadoView)

app_name = 'cartas'
urlpatterns = [
    path('pensionado/<int:pk>/', PensionadoDetailView.as_view(), name='pensionado_detalle'),
    path('pensionado/actualizar/<int:pk>', RegistroCreateView.as_view(), name='pensionado_actualizar'),
    path('pensionados-listado/<str:filtro>/', PensionadoListView.as_view(), name="pensionados_list"),
    # path('pensionado/generar-carta/', GenerarCartaView.as_view(), name='generar_carta'),
    # path('pensionado/generar-sobre/', GenerarSobreView.as_view(), name='generar_sobre'),
    path('pensionado/generar-archivos/', GenerarArchivosPensionadoView.as_view(), name='generar_archivos'),
    path('pensionado/buscar-monto/', BuscarMontoPlazoView.as_view(), name='buscar_monto'),
    path('plazos-listado/', PlazoListView.as_view(), name="plazos_list"),
    path('leer-reporte/', LeerReporteView.as_view(), name="leer_reporte"),
    path('alta-plazos/', AltaPlazos.as_view(), name="alta_plazos"),
    path('', Indice.as_view(), name='indice'),
]