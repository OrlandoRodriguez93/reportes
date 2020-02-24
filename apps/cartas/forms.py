#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from .models import Pensionado, Reporte, Credito, Deuda

class PensionadoForm(forms.ModelForm):

    capacidad = forms.CharField()
    liquido = forms.CharField()
    empresa = forms.CharField()
    cantidad_pagos = forms.CharField()
    cantidad = forms.CharField()

    class Meta:
        model = Pensionado
        fields = ('numero_social', 'nombre', 'edad', 'direccion', 'estado', 'ciudad')

    def __init__(self, *args, **kwargs):
        super(PensionadoForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class CreditoForm(forms.ModelForm):

    class Meta:
        model = Credito
        fields = ('capacidad', 'liquido')

    def __init__(self, *args, **kwargs):
        super(CreditoForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class DeudaForm(forms.ModelForm):

    class Meta:
        model = Deuda
        fields = ('empresa', 'cantidad_pagos', 'cantidad')

    def __init__(self, *args, **kwargs):
        super(DeudaForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class UploadDocumentForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ('reporte',)




