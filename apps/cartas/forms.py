#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from .models import Pensionado, Reporte, Credito, Deuda, Plazo, PLAZO_CHOICES


class PensionadoForm(forms.ModelForm):

    capacidad = forms.CharField()
    liquido = forms.CharField()
    meses_plazo = forms.ChoiceField(choices=PLAZO_CHOICES, required=False)
    monto_solicitado = forms.CharField(required=False)
    empresa = forms.CharField(required=False)
    cantidad_pagos = forms.CharField(required=False)
    cantidad = forms.CharField(required=False)

    class Meta:
        model = Pensionado
        fields = ('numero_social', 'nombre', 'edad', 'direccion', 'estado', 'ciudad')

    def __init__(self, *args, **kwargs):
        super(PensionadoForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class CreditoForm(forms.ModelForm):
    meses_plazo = forms.ChoiceField(choices= PLAZO_CHOICES, required=False)

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

class PlazoForm(forms.ModelForm):

    class Meta:
        model = Plazo
        fields = ('monto_solicitado', 'meses_plazo')

    def __init__(self, *args, **kwargs):
        super(PlazoForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class UploadDocumentForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ('reporte',)





