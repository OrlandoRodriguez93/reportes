#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import numpy
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, DeleteView, DetailView, View, UpdateView
from django.views.generic.edit import FormMixin
from django.db.models import Subquery

from docx import Document
from .models import Pensionado, Reporte, Credito, Deuda, Plazo
from .forms import PensionadoForm, UploadDocumentForm, CreditoForm, DeudaForm, PLAZO_CHOICES, PlazoForm
from .utils import ObtenerDatosPDFMixin, get_meses_plazo, get_id_meses_plazo

from django.shortcuts import render

from .utils import calcularEdad

"""
    Clase principal, muestra un template con las acciones a realizar
"""
class Indice(TemplateView):
    template_name = "cartas/indice.html"

class RegistroCreateView(UpdateView):
    template_name = "cartas/pensionado_actualizar.html"
    model = Pensionado
    form_class = PensionadoForm
    credito = None
    deuda = None
    plazo = None


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

    def get_plazo(self, id_plazo):
        if self.plazo is None and id_plazo is not None:
            if Plazo.objects.filter(pk=id_plazo).count() > 0:
                self.plazo = Plazo.objects.get(pk=id_plazo)
        return self.plazo

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
        context['capacidad'] = int(self.credito.capacidad)

        try:
            self.plazo = self.get_plazo(self.credito.id_plazo)
            if self.plazo is not None:
                plazo_form = PlazoForm()
                plazo_form.fields["meses_plazo"].initial = PLAZO_CHOICES[get_id_meses_plazo(int(self.plazo.meses_plazo))]
                plazo_form.fields["monto_solicitado"].initial = self.plazo.monto_solicitado
                context['plazo_form'] = plazo_form
        except:
            pass

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
        try:
            meses_plazo = str(get_meses_plazo(int(form.cleaned_data['meses_plazo'])))
            monto_solicitado = form.cleaned_data['monto_solicitado'] if form.cleaned_data['monto_solicitado'] != '' else 0
            id_plazo = Plazo.objects.get(meses_plazo=meses_plazo, monto_solicitado=Decimal(monto_solicitado)).pk
            credito.id_plazo = id_plazo
        except:
            pass

        deuda = self.get_deuda(self.object.pk)
        if deuda is not None:
            deuda.empresa = form.cleaned_data['empresa']
            deuda.cantidad_pagos = form.cleaned_data['cantidad_pagos']
            deuda.cantidad = form.cleaned_data['cantidad']
            
        self.object.save() 
        credito.save(update_fields=['capacidad', 'liquido', 'id_plazo'])

        if deuda is not None:
            deuda.save(update_fields=['empresa', 'cantidad_pagos', 'cantidad'])     

        return redirect(reverse('cartas:pensionado_detalle', kwargs={'pk':self.object.pk}))

    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

class PensionadoListView(ListView):
    paginate_by = 20
    model = Pensionado
    context_object_name = 'pensionados'
    template_name = "cartas/pensionados_listado.html"
    ordering = ['-creado']
    active = 'todos'

    def get_queryset(self):
        filtro = self.kwargs['filtro']

        if filtro == 'conarchivos':
            pensionados = Pensionado.objects.filter(carta_generada=True, sobre_generado=True, estatus_registro=0).order_by('-creado')
            self.active = 'conarchivos'
        elif filtro == 'sinarchivos':
            pensionados = Pensionado.objects.filter(carta_generada=False, sobre_generado=False, estatus_registro=0).order_by('-creado')
            self.active = 'sinarchivos'
        else:
            pensionados = Pensionado.objects.filter(estatus_registro=0)
            self.active = 'todos'
        return pensionados

    def get_context_data(self, **kwargs):
        context = super(PensionadoListView, self).get_context_data(**kwargs)
        context['activo'] = self.active
        return context

    # def get_queryset(self):
    #     return Pensionado.objects.filter(estatus_registro=0)

class PensionadoDetailView(DetailView):
    model = Pensionado
    template_name = "cartas/pensionado_detalle.html"
    credito = None
    deuda = None
    plazo = None

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
    
    def get_plazo(self, id_plazo):
        if self.plazo is None and id_plazo is not None:
            if Plazo.objects.filter(pk=id_plazo).count() > 0:
                self.plazo = Plazo.objects.get(pk=id_plazo)
        return self.plazo

    def get(self, request, *args, **kwargs):
        pensionado = get_object_or_404(Pensionado, pk=kwargs['pk'])
        context = {}
        context['pensionado'] = pensionado
        context['credito'] = self.get_credito(self.kwargs['pk'])
        context['deuda'] = self.get_deuda(self.kwargs['pk'])
        context['plazo'] = self.get_plazo(self.credito.id_plazo)
        return render(request, 'cartas/pensionado_detalle.html', context)

class LeerReporteView(CreateView, FormMixin, ObtenerDatosPDFMixin):
    template_name = "cartas/leer_reporte.html"
    model = Reporte
    form_class = UploadDocumentForm
    success_url = "cartas/pensionado_actualizar.html"
    BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'media')
    contenido = []
    datos_pensionado = {}

    def get_context_data(self, **kwargs):
        context = super(LeerReporteView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        self.datos_pensionado = {}
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

        return redirect(reverse('cartas:pensionado_actualizar', kwargs={'pk':pensionado.pk}))

class PlazoListView(ListView):
    model = Plazo
    context_object_name = 'plazos'
    template_name = "cartas/plazos_listado.html"
    ordering = ['creado']

    def get_context_data(self, **kwargs):
        context = super(PlazoListView, self).get_context_data(**kwargs)
        context['plazos'] = self.obtener_listado_montos()
        return context

    def obtener_listado_montos(self):
        listado_dict = {}
        for result in Plazo.objects.values('monto_solicitado', 'meses_plazo', 'pago').order_by('monto_solicitado', 'meses_plazo').distinct():
            try:
                listado_dict[str(result['monto_solicitado'])].append([result['meses_plazo'], str(result['pago'])])
            except:
                listado_dict[str(result['monto_solicitado'])] = []
                listado_dict[str(result['monto_solicitado'])].append([result['meses_plazo'], str(result['pago'])])

        return listado_dict


class AltaPlazos(CreateView, FormMixin, ObtenerDatosPDFMixin):
    template_name = "cartas/alta_plazos.html"
    model = Reporte
    form_class = UploadDocumentForm
    success_url = "cartas/plazos_listado.html"
    BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'media')
    contenido = []
    datos_pensionado = {}

    def get_context_data(self, **kwargs):
        context = super(AltaPlazos, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()

        ruta = os.path.join(self.BASE, str(self.object.reporte))
        ruta_pdf = ruta.replace('/apps','')

        if os.path.isfile(ruta_pdf):  
            ruta_csv = self.generar_archivo_cotizador(ruta_pdf)
            self.modificar_cotizador_csv(ruta_csv)
            self.generar_plazos_actuales(ruta_csv)

        return redirect(reverse('cartas:plazos_list'))

# class GenerarCartaView(ObtenerDatosPDFMixin, View):
    
#     def post(self, request, *args, **kwargs):
#         id_pensionado = request.POST.get('id_pensionado')
#         try:
#             credito = Credito.objects.get(id_pensionado=id_pensionado)
#             plazo = Plazo.objects.get(pk=credito.id_plazo)
#         except ObjectDoesNotExist:
#             mensaje = "No existe un plazo para este pensionado. Selecciona un plazo en el detalle del pensionado."
#             return JsonResponse({"success":False, "message":mensaje}, status=400)

#         try:    
#             pensionado = Pensionado.objects.get(pk=id_pensionado)
#             self.sobreescribir_carta(pensionado.nombre, str(plazo.monto_solicitado))
#         except:
#             mensaje = "No se pudo generar la carta para el pensionado."
#             return JsonResponse({"success":False, "message":mensaje}, status=400)
#         return JsonResponse({"success":True}, status=200)


# class GenerarSobreView(ObtenerDatosPDFMixin, View):
    
#     def post(self, request, *args, **kwargs):
#         id_pensionado = request.POST.get('id_pensionado')
#         try:    
#             pensionado = Pensionado.objects.get(pk=id_pensionado)
#             self.sobreescribir_sobre(pensionado.nombre, pensionado.direccion)
#         except:
#             mensaje = "No se pudo generar el sobre para el pensionado."
#             return JsonResponse({"success":False, "message":mensaje}, status=400)
#         return JsonResponse({"success":True}, status=200)

class GenerarArchivosPensionadoView(ObtenerDatosPDFMixin, View):
    def post(self, request, *args, **kwargs):
        id_pensionado = request.POST.get('id_pensionado')
        # Buscamos el plazo y el monto del credito para el pensionado
        try:
            credito = Credito.objects.get(id_pensionado=id_pensionado)
            plazo = Plazo.objects.get(pk=credito.id_plazo)
        except ObjectDoesNotExist:
            mensaje = "No existe un plazo para este pensionado. Selecciona un plazo en el detalle del pensionado."
            return JsonResponse({"success":False, "message":mensaje}, status=400)
        # Obtenemos el pensionado y generamos la carta y el sobre
        try:    
            pensionado = Pensionado.objects.get(pk=id_pensionado)
            self.sobreescribir_carta(pensionado.nombre, str(plazo.monto_solicitado))
            self.sobreescribir_sobre(pensionado.nombre, pensionado.direccion)
            pensionado.carta_generada = True
            pensionado.sobre_generado = True
            pensionado.save(update_fields=['carta_generada', 'sobre_generado'])
        except:
            mensaje = "Algún archivo no pudo ser generado correctamente."
            return JsonResponse({"success":False, "message":mensaje}, status=400)
        return JsonResponse({"success":True}, status=200)


class BuscarMontoPlazoView(View):
    
    def post(self, request, *args, **kwargs):
        id_pensionado = request.POST.get('id_pensionado')
        id_plazo = request.POST.get('plazo')
        meses_plazo = get_meses_plazo(int(id_plazo))

        try:
            credito = Credito.objects.get(id_pensionado=id_pensionado)
            capacidad = credito.capacidad
            if capacidad != 0:
                plazos_list = Plazo.objects.filter(meses_plazo=meses_plazo).values_list('pk', 'pago')

                for idx, plazo in enumerate(plazos_list):
                    if plazo[1] >= capacidad:
                        monto = Plazo.objects.get(pk=plazo[0]).monto_solicitado
                        credito.id_plazo = plazos_list[idx][0]
                        credito.save(update_fields=['id_plazo'])
                        break
            else:
                monto = 0.00
        except:
            mensaje = "No existe un plazo para este pensionado. Selecciona un plazo en el detalle del pensionado."
            return JsonResponse({"success":False, "message":mensaje}, status=400)
        return JsonResponse({"success":True, 'monto':monto}, status=200)