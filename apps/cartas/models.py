#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone

class Pensionado(models.Model):

    numero_social = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField(null=True)
    direccion = models.CharField(max_length=200)
    estado = models.CharField(max_length=50)
    ciudad = models.CharField(max_length=50)
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
    id_pensionado = models.IntegerField(null=True)
    capacidad = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    liquido = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    id_plazo = models.IntegerField(null=True)
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now_add=True)
    estatus_registro = models.IntegerField(default=0)

    def __str__(self):
        return "capacidad: %s" % (self.capacidad)

    def save(self, *args, **kwargs):
        self.actualizado = timezone.now()
        super(Credito, self).save(*args, **kwargs) 

class Deuda(models.Model):
    id_pensionado = models.IntegerField(null=True)
    empresa = models.CharField(max_length=100, null=True)
    cantidad_pagos = models.CharField(max_length=100, default="0/0")
    cantidad = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now_add=True)
    estatus_registro = models.IntegerField(default=0)

    def __str__(self):
        return "empresa: %s" % (self.empresa)

    def save(self, *args, **kwargs):
        self.actualizado = timezone.now()
        super(Deuda, self).save(*args, **kwargs) 


class Plazo(models.Model):
    meses_plazo = models.IntegerField()
    cantidad_a_prestar = models.DecimalField(max_digits=15, decimal_places=2)
    cantidad_pensionado = models.DecimalField(max_digits=15, decimal_places=2)
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now_add=True)
    estatus_registro = models.IntegerField(default=0)

    def __str__(self):
        return "meses: %s" % (self.meses_plazo)

    def save(self):
        self.actualizado = timezone.now()
        super(Plazo, self).save(*args, **kwargs) 

