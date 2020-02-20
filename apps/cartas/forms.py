#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from .models import Pensionado, Reporte

class PensionadoForm(forms.ModelForm):

    class Meta:
        model = Pensionado
        fields = ('numero_social', 'nombre', 'edad', 'direccion', 'estado', 'ciudad')

    def __init__(self, *args, **kwargs):
        super(PensionadoForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class UploadDocumentForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ('reporte',)




