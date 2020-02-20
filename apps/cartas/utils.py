#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import date 

# YYYY/MM/DD
def calcularEdad(fecha): 
    today = date.today() 
    age = today.year - fecha.year - ((today.month, today.day) < (fecha.month, fecha.day)) 
    return age 


# 
# 600810


