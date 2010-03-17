#!/usr/bin/python
import csv
import sys
import os
import datetime
import time
import re

sys.path.append('/home/sistema/aplicacion/deudor')
os.environ['DJANGO_SETTINGS_MODULE']='settings'

from core.models import *
from core.views import loadData


data =csv.reader(open(sys.argv[1],"r"), delimiter=',')
lines = ''

for row in data:
    #Ver si el nombre viene con 
    # Apellidos - Nombres o al reves
    apellidos = ''
    nombres = ''
    d_nombres = row[0]
    nombres_apellidos = \
        [  a for a in  d_nombres.split(" ") if a!= ""]

    if (int(row[1].strip()[:-1]) == int(row[2].strip()[:-2])):
        #Entonces la data es apellidos-nombres
        apellidos =  " ".join(nombres_apellidos[0:2]) 
        nombres = " ".join(nombres_apellidos[2:])

    else:
        #La data viene nombre-apellidos
        apellidos =  " ".join(nombres_apellidos[1:]) 
        nombres = " ".join(nombres_apellidos[:-2])
                
    rut = int(row[1].strip()[:-1])

    direccion = "%s %s " % (row[3].strip().replace(",",""), row[4].strip().replace(",",""))

    telefono = row[5].strip()
    #if row[9].strip() != "":
    #    telefono = row[8][4:]+"-"+row[9].strip()

    celular = row[8].strip()

    deuda = 0

    vencimientos = row[11].strip().split('-')
    vencimiento = ''
    if len(vencimientos) == 3:
        vencimiento = vencimientos[2]+vencimientos[1]+vencimientos[0]

    fechas = row[10].strip().split('-')
    fecha = fechas[2] + fechas[1] + fechas[0]
    
    line = "%s,%s,%s,%s,%s,%s,%s,%s,%s" % (rut, apellidos, nombres, direccion, telefono, celular, deuda, vencimiento, fecha)

    load_res = loadData(line)

    res = "ya existe"

    if 'ficha' in load_res:
        res = "  Ficha creada"

    if 'persona' in load_res:
        res = " Persona creada"

    if 'ficha' in load_res and 'persona' in load_res:
        res = 'Persona y Ficha creadas'

    if 'actualizada' in load_res:
        res = 'Datos actualizados'
            
    line = "%s,%s,%s,%s" % (rut, apellidos, nombres, res)
    print line
    
