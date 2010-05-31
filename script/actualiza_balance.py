#!/usr/bin/python
import sys
import os
import datetime
import time


sys.path.append('/home/fmardones/deudor/deudor')
os.environ['DJANGO_SETTINGS_MODULE']='settings'

from django.db.models import Q
from core.models import *


fichas = Ficha.objects.all()
for laficha in fichas:
    gastos=0
    try:
        balance = Balance.objects.get(laficha)
    except:
        balance = Balance(ficha = laficha)

    balance.fecha=datetime.now()
    balance.capital=laficha.deuda_inicial
    eventos = Evento.objects.filter(ficha = laficha.id, gasto_judicial__isnull=False)
    for e in eventos:
        gastos += int(e.gasto_judicial)
    if gastos > 0: print '%s %d' %  (laficha.persona_id, gastos)
    balance.costas = gastos
    balance.save()
        

    
