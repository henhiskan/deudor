#!/usr/bin/python
import csv
import sys
import os
import datetime
import time
import re
import signal

sys.path.append('/home/rrossel/Personal/Proyectos/deudor/deudor')
os.environ['DJANGO_SETTINGS_MODULE']='settings'
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

from core.models import *
from core.views import loadData


data =csv.reader(open(sys.argv[1],"r"), delimiter=';')
lines = ''

for row in data:
    rut = row[0]
    fecha = False
    if row[1]:
        try:
            fecha =  datetime.datetime(*time.strptime(row[1],'%d/%m/%Y')[0:3])
        except:
            print "Deudor %s, Fecha ficha no existe o mal formada " % \
                ( rut )
	    print "Fecha:", row[1]
            continue

    orden = row[2]
    codigo_id = row[3]
    descripcion = row[4]
    fecha_proximo_pago = False
    if row[5]:
        fecha_proximo_pago = datetime.datetime(*time.strptime(row[5],'%d/%m/%Y')[0:3])
    forma_pago = row[6]
    capital = row[7]
    interes = row[8]
    costas = row[9]
    honorario = row[10]
    gasto_jud = row[11]
    id_receptor = row[12]
    id_tribunal = row[13]
    
    # Busqueda del deudor
    deudor = False
    try:
        deudor = Persona.objects.get(rut=rut)
    except:
        print " %s Rut no encontrado " % (rut) 
        continue

    ficha = deudor.ficha_set.all()[0]
    if not ficha:
        print " Ficha para deudor %s no existe " % (rut)
        continue

    #Busqueda de codigo
    codigo=False
    if codigo_id:
        try:
            codigo = Codigo.objects.get(codigo_id = codigo_id)
        except:
            print "Deudor %s, no existe codigo %s" % \
                (rut, codigo_id)
            continue
    else:
        print "Deudor %s, No existe codigo " % (rut)
        continue

    #Busqueda de Forma Pago
    if forma_pago:
        try:
            forma_pago = FormaPago.objects.get(codigo=forma_pago)
        except:
            print "Deudor %s, No existe forma de pago con codigo %"\
                % ( rut, forma_pago)
            pass

    #Busqueda de Receptor
    receptor = False
    if id_receptor:
        try:
            receptor = Receptor.objects.get(id=id_receptor)
        except:
            print "Deudor %s, No existe receptor con id %s" \
                % ( rut, id_receptor)
        
    evento = Evento(ficha=ficha, 
                    fecha=fecha,
                    codigo=codigo)
    if fecha:
        evento.fecha = fecha
    if orden:
        evento.orden = orden
    if fecha_proximo_pago:
        evento.proximo_pago = fecha_proximo_pago
    if descripcion:
        evento.descripcion = descripcion
    if forma_pago:
        evento.forma_pago = forma_pago
    if capital:
        evento.capital = capital
    if gasto_jud:
        evento.gasto_judicial = gasto_jud
    if honorario:
        evento.honorario = honorario
    if interes:
        evento.interes = interes
    if costas:
        evento.costas = costas
    if receptor:
        evento.receptor = receptor
        
        
    #Guardando en BD
    evento.save()
    print "Nuevo Evento para deudor %s guardado" % \
        ( rut )
