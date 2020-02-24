#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import PyPDF2
import tabula
import numpy
import csv
from decimal import Decimal
from datetime import date
from docx import Document

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'media')

# YYYY/MM/DD
def calcularEdad(fecha): 
    today = date.today() 
    age = today.year - fecha.year - ((today.month, today.day) < (fecha.month, fecha.day)) 
    return age 

class ObtenerDatosPDFMixin(object):
    contenido = []

    def convertir_csv(self, ruta_pdf):
            df = tabula.read_pdf(ruta_pdf ,multiple_tables=True)
            # Convertimos el archivo a formato CSV y lo guardamos 
            ruta_csv = os.path.join(BASE, str("archivo.csv"))
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
            capacidad_titulo = numpy.where(numpy.char.find(contenido_array, 'CAPACIDAD DE CR?DITO')>=0)
            capacidad = self.contenido[capacidad_titulo[0][0] - 1][2][2:]
            capacidad = capacidad.split('$')[0].strip()
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


def sobreescribir_carta(nombre_pensionado, cantidad_prestamo):
    # ruta_carta = '/Users/macbookair/Reportes/reportes/static/media/formatos/formato_carta.docx'
    # BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'media')
    ruta_carta = os.path.join(BASE, str("formatos/formato_carta.docx"))
    ruta_carta = ruta_carta.replace('/apps','')

    doc = Document(ruta_carta)
    for p in doc.paragraphs:
        if 'NOMBRE' in p.text:
            inline = p.runs
            for i in range(len(inline)):
                if 'NOMBRE' in inline[i].text:
                    text = inline[i].text.replace('NOMBRE', nombre_pensionado)
                    inline[i].text = text
        if 'CANTIDAD' in p.text:
            inline = p.runs
            for i in range(len(inline)):
                if 'CANTIDAD' in inline[i].text:
                    text = inline[i].text.replace('CANTIDAD', cantidad_prestamo)
                    inline[i].text = text
    today = date.today() 
    fecha = str(today.year) + str(today.month)    

    ruta_guardado = os.path.join(BASE, str("cartas/"+ fecha))
    ruta_guardado = ruta_guardado.replace('/apps','')
    
    # ruta_guardado = '/Users/macbookair/Reportes/reportes/static/media/cartas/'+ fecha
    
    if not os.path.exists(ruta_guardado):
        os.makedirs(ruta_guardado)
    doc.save(ruta_guardado + '/carta_' + nombre_pensionado + '.docx')

def sobreescribir_sobre(nombre_pensionado, direccion_envio):
    # ruta_sobre = '/Users/macbookair/Reportes/reportes/static/media/formatos/formato_sobre.docx'
    # BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'media')
    ruta_sobre = os.path.join(BASE, str("formatos/formato_sobre.docx"))
    ruta_sobre = ruta_sobre.replace('/apps','')

    doc = Document(ruta_sobre)
    for p in doc.paragraphs:
        if 'NOMBRE' in p.text:
            inline = p.runs
            for i in range(len(inline)):
                if 'NOMBRE' in inline[i].text:
                    text = inline[i].text.replace('NOMBRE', nombre_pensionado)
                    inline[i].text = text
        if 'DIRECCION' in p.text:
            inline = p.runs
            for i in range(len(inline)):
                if 'DIRECCION' in inline[i].text:
                    text = inline[i].text.replace('DIRECCION', direccion_envio)
                    inline[i].text = text
    today = date.today() 
    fecha = str(today.year) + str(today.month)    

    ruta_guardado = os.path.join(BASE, str("sobres/"+ fecha))
    ruta_guardado = ruta_guardado.replace('/apps','')
    
    # ruta_guardado = '/Users/macbookair/Reportes/reportes/static/media/sobres/'+ fecha
    
    if not os.path.exists(ruta_guardado):
        os.makedirs(ruta_guardado)
    doc.save(ruta_guardado + '/sobre_' + nombre_pensionado + '.docx')