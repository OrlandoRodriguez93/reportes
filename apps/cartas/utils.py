#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
from datetime import date
from docx import Document

BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'media')

# YYYY/MM/DD
def calcularEdad(fecha): 
    today = date.today() 
    age = today.year - fecha.year - ((today.month, today.day) < (fecha.month, fecha.day)) 
    return age 


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