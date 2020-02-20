#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import PyPDF2
import tabula
import numpy
import csv
from datetime import date 
from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, DeleteView, DetailView, View
from django.views.generic.edit import FormMixin

from .models import Pensionado, Reporte, Credito, Deuda
from .forms import PensionadoForm, UploadDocumentForm

from django.shortcuts import render

from .utils import calcularEdad

"""
    Clase principal, muestra un template con las acciones a realizar
"""
class Indice(TemplateView):
    template_name = "cartas/indice.html"

class RegistroCreateView(CreateView):
    template_name = "cartas/nuevo_registro.html"
    model = Pensionado
    form_class = PensionadoForm
    success_url = "cartas/pensionados_listado.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        credito = Credito.objects.get(id_pensionado=kwargs['pk'])
        context['credito'] = credito
        return context

    def get(self, request, *args, **kwargs):
        context = {}
        pensionado = get_object_or_404(Pensionado, pk=kwargs['pk'])
        context['pensionado'] = PensionadoForm(instance=pensionado)
        
        credito = Credito.objects.get(id_pensionado=kwargs['pk'])
        context['credito'] = credito

        try:
            deuda = Deuda.objects.get(id_pensionado=kwargs['pk'])
            context['deuda'] = deuda
        except:
            pass
        return render(request, 'cartas/nuevo_registro.html', context)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return HttpResponseRedirect(reverse('cartas:pensionados_list'))

class PensionadoListView(ListView):
    model = Pensionado
    context_object_name = 'pensionados'
    template_name = "cartas/pensionados_listado.html"

    # def get_queryset(self):
    #     filtro = self.request.GET.get('filtro', 'nombre')
    #     new_context = Pensionado.objects.filter(nombre=filtro,)
    #     return new_context

    # def get_context_data(self, **kwargs):
    #     context = super(PensionadoListView, self).get_context_data(**kwargs)
    #     context['filter'] = self.request.GET.get('filter', 'nombre')
    #     return context

class PensionadoDetailView(DetailView):
    model = Pensionado
    template_name = "cartas/pensionado_detalle.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        pensionado = get_object_or_404(Pensionado, pk=kwargs['pk'])
        context = {'pensionado': pensionado}
        return render(request, 'cartas/pensionado_detalle.html', context)

class LeerReporteView(CreateView, FormMixin):
    template_name = "cartas/leer_reporte.html"
    model = Reporte
    form_class = UploadDocumentForm
    success_url = "cartas/nuevo_registro.html"
    BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'media')
    contenido = []
    datos_pensionado = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()

        ruta = os.path.join(self.BASE, str(self.object.reporte))
        ruta_pdf = ruta.replace('/apps','')

        if os.path.isfile(ruta_pdf):  
            ruta_csv = self.convertir_csv(ruta_pdf)
            self.leer_csv(ruta_csv)
            self.obtener_datos_csv()

        pensionado = Pensionado.objects.create()
        pensionado.numero_social = self.datos_pensionado['numero_social']
        pensionado.nombre = self.datos_pensionado['nombre']
        pensionado.edad = int(self.datos_pensionado['edad'])
        pensionado.direccion = self.datos_pensionado['domicilio']
        pensionado.ciudad = self.datos_pensionado['ciudad']
        pensionado.estado = self.datos_pensionado['estado']
        pensionado.save()

        self.object.id_pensionado = pensionado.pk
        self.object.save(update_fields=['id_pensionado'])

        credito = Credito.objects.create()
        capacidad = self.datos_pensionado['capacidad'].replace(",","")
        liquido = self.datos_pensionado['liquido'].replace(",","")
        credito.id_pensionado = pensionado.pk
        credito.capacidad = float(capacidad)
        credito.liquido = float(liquido)
        credito.save()

        if 'deuda_empresa' in self.datos_pensionado:
            deuda = Deuda.objects.create()
            deuda.id_pensionado = pensionado.pk
            deuda.empresa = self.datos_pensionado['deuda_empresa']
            deuda.cantidad_pagos = self.datos_pensionado['deuda_cantidad_pagos']
            cantidad = self.datos_pensionado['deuda_cantidad'].replace(",","")
            deuda.cantidad = float(cantidad)
            deuda.save()

    
        return redirect(reverse('cartas:nuevo_registro', kwargs={'pk':pensionado.pk}))

    def convertir_csv(self, ruta_pdf):
        df = tabula.read_pdf(ruta_pdf ,multiple_tables=True)
        # Convertimos el archivo a formato CSV y lo guardamos 
        ruta_csv = os.path.join(self.BASE, str("archivo.csv"))
        ruta_csv = ruta_csv.replace('/apps','')
        tabula.convert_into(ruta_pdf, ruta_csv, output_format="csv", stream=True, pages=1)

        return ruta_csv

    def leer_csv(self, ruta_csv):
        self.contenido = []
        f = open(ruta_csv)
        
        csv_f = csv.reader(f)
        for index, row in enumerate(csv_f):
            self.contenido.append(list(row[i] for i in [0,1,2,3,4]))

    def obtener_datos_csv(self):
        contenido_array = numpy.array(self.contenido)

        nss = numpy.where(contenido_array == 'NSS')
        numero_social = self.contenido[nss[0][0] - 1][0]

        nombre_titulo = numpy.where(contenido_array == 'NOMBRE DEL ASEGURADO')
        nombre = self.contenido[nombre_titulo[0][0] - 1][2]

        try:
            estado_titulo = numpy.where(contenido_array == 'DELEGACI?N DE PAGO')
            estado = self.contenido[estado_titulo[0][0] - 1][3]
        except:
            estado_titulo = numpy.where(contenido_array == 'FECHA DE  VENCIMIENTO DELEGACI?N DE PAGO')
            estado = self.contenido[estado_titulo[0][0] - 1][2][16:]

        ciudad_titulo = numpy.where(contenido_array == 'SUBDELEGACI?N DE PAGO')
        ciudad = self.contenido[ciudad_titulo[0][0] - 1][4]

        domicilio_titulo = numpy.where(contenido_array == 'DOMICILIO')
        domicilio = self.contenido[domicilio_titulo[0][0] - 1][2]
        if domicilio == '':
            domicilio = self.contenido[domicilio_titulo[0][0] - 1][1]
            if domicilio == '':
                domicilio = self.contenido[domicilio_titulo[0][0] - 1][0]

        curp_titulo = numpy.where(contenido_array == 'CURP')
        curp = self.contenido[curp_titulo[0][0] - 1][4]
        fecha_nacimiento_curp = curp[4:10]
        # Se espera que todos los registros contengan una fecha de nacimiento a mayor al año 2000 (en el 2020)
        # el CURP solo devuelve 2 dígitos del año de nacimiento, agregamos manualmente el 19** faltante
        fecha_nacimiento = date(int('19' + fecha_nacimiento_curp[0:2]), int(fecha_nacimiento_curp[3:4]), int(fecha_nacimiento_curp[4:6]))
        edad = calcularEdad(fecha_nacimiento)

        liquido_titulo = numpy.where(contenido_array == 'L?QUIDO')
        liquido = self.contenido[liquido_titulo[0][0] - 1][4][2:]

        try:
            if contenido_array == 'CAPACIDAD DE CR?DITO':
                capacidad_titulo = numpy.where(numpy.char.find(contenido_array, 'CAPACIDAD DE CR?DITO')>=0)
                capacidad = self.contenido[capacidad_titulo[0][0] - 1][2][2:]
            # elif contenido_array == 'CUENTA CLABE CAPACIDAD DE CR?DITO PERCEPCIONES':
            #     capacidad_titulo = numpy.where(contenido_array == 'CUENTA CLABE CAPACIDAD DE CR?DITO PERCEPCIONES')
            #     capacidad = self.contenido[capacidad_titulo[0][0] - 1][2][2:]
            # elif contenido_array == 'CUENTA CLABE CAPACIDAD DE CR?DITO':
            #     capacidad_titulo = numpy.where(contenido_array == 'CUENTA CLABE CAPACIDAD DE CR?DITO')
            #     capacidad = self.contenido[capacidad_titulo[0][0] - 1][2][2:]
        except: 
            capacidad = '-9999.0'

        deuda_concepto = numpy.where(numpy.char.find(contenido_array, '301 PRESTAMO')>=0)

        if deuda_concepto[0].any():
            deuda_empresa = self.contenido[deuda_concepto[0][0]][0][15:]
            deuda_cantidad_pagos = self.contenido[deuda_concepto[0][0]][3]
            deuda_cantidad = self.contenido[deuda_concepto[0][0]][4][3:]

            self.datos_pensionado['deuda_empresa'] = deuda_empresa
            self.datos_pensionado['deuda_cantidad_pagos'] = deuda_cantidad_pagos
            self.datos_pensionado['deuda_cantidad'] = deuda_cantidad


        self.datos_pensionado['numero_social'] = numero_social
        self.datos_pensionado['nombre'] = nombre
        self.datos_pensionado['estado'] = estado
        self.datos_pensionado['ciudad'] = ciudad
        self.datos_pensionado['domicilio'] = domicilio
        self.datos_pensionado['edad'] = edad
        self.datos_pensionado['liquido'] = liquido
        self.datos_pensionado['capacidad'] = capacidad
        
