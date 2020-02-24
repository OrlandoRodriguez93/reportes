#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, DeleteView, DetailView, View, UpdateView
from django.views.generic.edit import FormMixin

from docx import Document
from .models import Pensionado, Reporte, Credito, Deuda
from .forms import PensionadoForm, UploadDocumentForm, CreditoForm, DeudaForm
from .utils import ObtenerDatosPDFMixin, sobreescribir_carta, sobreescribir_sobre

from django.shortcuts import render

from .utils import calcularEdad

"""
    Clase principal, muestra un template con las acciones a realizar
"""
class Indice(TemplateView):
    template_name = "cartas/indice.html"

class RegistroCreateView(UpdateView):
    template_name = "cartas/nuevo_registro.html"
    model = Pensionado
    form_class = PensionadoForm
    success_url = "cartas/pensionados_listado.html"
    credito = None
    deuda = None


    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form = form))

    def get_deuda(self, pk):
        if self.deuda is None:
            if Deuda.objects.filter(id_pensionado=pk).count() > 0:
                self.deuda = Deuda.objects.get(id_pensionado=pk)
        return self.deuda

    def get_credito(self, pk):
        if self.credito is None:
            if Credito.objects.filter(id_pensionado=pk).count() > 0:
                self.credito = Credito.objects.get(id_pensionado=pk)
        return self.credito

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super(RegistroCreateView, self).get_context_data(**kwargs)
        credito_form = CreditoForm()

        pensionado = get_object_or_404(Pensionado, pk=self.kwargs['pk'])
        context['pensionado'] = PensionadoForm(instance=pensionado)
        
        self.credito = self.get_credito(self.kwargs['pk'])
        credito_form.fields["capacidad"].initial = self.credito.capacidad
        credito_form.fields["liquido"].initial = self.credito.liquido
        context['credito_form'] = credito_form

        try:
            self.deuda = self.get_deuda(self.kwargs['pk'])
            if self.deuda is not None:
                deuda_form = DeudaForm()
                deuda_form.fields["empresa"].initial = self.deuda.empresa
                deuda_form.fields["cantidad_pagos"].initial = self.deuda.cantidad_pagos
                deuda_form.fields["cantidad"].initial = self.deuda.cantidad
                context['deuda_form'] = deuda_form
        except:
            pass

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)

        credito = self.get_credito(self.object.pk)
        credito.capacidad = form.cleaned_data['capacidad']
        credito.liquido = form.cleaned_data['liquido']

        deuda = self.get_deuda(self.object.pk)
        if deuda is not None:
            deuda.empresa = form.cleaned_data['empresa']
            deuda.cantidad_pagos = form.cleaned_data['cantidad_pagos']
            deuda.cantidad = form.cleaned_data['cantidad']
            
        self.object.save() 
        credito.save(update_fields=['capacidad', 'liquido'])

        if deuda is not None:
            deuda.save(update_fields=['empresa', 'cantidad_pagos', 'cantidad'])     
        
        return redirect(reverse('cartas:pensionado_detalle', kwargs={'pk':self.object.pk}))

    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

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
    credito = None
    deuda = None

    def get_deuda(self, pk):
        if self.deuda is None:
            if Deuda.objects.filter(id_pensionado=pk).count() > 0:
                self.deuda = Deuda.objects.get(id_pensionado=pk)
        return self.deuda

    def get_credito(self, pk):
        if self.credito is None:
            if Credito.objects.filter(id_pensionado=pk).count() > 0:
                self.credito = Credito.objects.get(id_pensionado=pk)
        return self.credito

    def get(self, request, *args, **kwargs):
        pensionado = get_object_or_404(Pensionado, pk=kwargs['pk'])
        context = {}
        context['pensionado'] = pensionado
        context['credito'] = self.get_credito(self.kwargs['pk'])
        context['deuda'] = self.get_deuda(self.kwargs['pk'])
        return render(request, 'cartas/pensionado_detalle.html', context)

class LeerReporteView(CreateView, FormMixin, ObtenerDatosPDFMixin):
    template_name = "cartas/leer_reporte.html"
    model = Reporte
    form_class = UploadDocumentForm
    success_url = "cartas/nuevo_registro.html"
    BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'media')
    contenido = []
    datos_pensionado = {}

    def get_context_data(self, **kwargs):
        context = super(LeerReporteView, self).get_context_data(**kwargs)
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
        #modificar
        sobreescribir_carta(pensionado.nombre, str(credito.capacidad))

        return redirect(reverse('cartas:nuevo_registro', kwargs={'pk':pensionado.pk}))

    