#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone

PLAZO_CHOICES =( 
    ("1", "24"), 
    ("2", "36"), 
    ("3", "48"), 
    ("4", "60"),
) 

class Pensionado(models.Model):

    numero_social = models.CharField(max_length=20, blank=True)
    nombre = models.CharField(max_length=100, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    estado = models.CharField(max_length=50, blank=True)
    ciudad = models.CharField(max_length=50, blank=True)
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now_add=True)
    estatus_registro = models.IntegerField(default=0)

    def __str__(self):
        return "nombre: %s , edad: %s" % (self.nombre, self.edad)

    def save(self, *args, **kwargs):
        self.actualizado = timezone.now()
        super(Pensionado, self).save(*args, **kwargs) 


class Reporte(models.Model):
    id_pensionado = models.CharField(max_length=255, blank=True, null=True)
    reporte = models.FileField(upload_to='documentos/')
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now_add=True)
    estatus_registro = models.IntegerField(default=0)

    def __str__(self):
        return "reporte: %s" % (self.reporte)

    def save(self, *args, **kwargs):
        self.actualizado = timezone.now()
        super(Reporte, self).save(*args, **kwargs) 


class Credito(models.Model):
    id_pensionado = models.IntegerField(null=True, blank=True)
    capacidad = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    liquido = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    id_plazo = models.IntegerField(null=True, blank=True)
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now_add=True)
    estatus_registro = models.IntegerField(default=0)

    def __str__(self):
        return "capacidad: %s" % (self.capacidad)

    def save(self, *args, **kwargs):
        self.actualizado = timezone.now()
        super(Credito, self).save(*args, **kwargs) 

class Deuda(models.Model):
    id_pensionado = models.IntegerField(null=True, blank=True)
    empresa = models.CharField(max_length=100, null=True, blank=True)
    cantidad_pagos = models.CharField(max_length=100, default="0/0", blank=True)
    cantidad = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now_add=True)
    estatus_registro = models.IntegerField(default=0)

    def __str__(self):
        return "empresa: %s" % (self.empresa)

    def save(self, *args, **kwargs):
        self.actualizado = timezone.now()
        super(Deuda, self).save(*args, **kwargs) 


class Plazo(models.Model):
    meses_plazo = models.CharField(max_length=2, choices=PLAZO_CHOICES, blank=True, default="48", null=True)
    monto_solicitado = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    pago = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now_add=True)
    estatus_registro = models.IntegerField(default=0)

    def __str__(self):
        return "meses: %s - monto: %s" % (self.meses_plazo, self.monto_solicitado)
    
    def save(self, *args, **kwargs):
        self.actualizado = timezone.now()
        super(Plazo, self).save(*args, **kwargs) 

