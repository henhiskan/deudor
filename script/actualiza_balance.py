#!/usr/bin/python
import sys
import os
import datetime
import time


sys.path.append('/home/fmardones/deudor/deudor')
os.environ['DJANGO_SETTINGS_MODULE']='settings'

from core.models import *

fichas = Ficha.objects.all()
for laficha in fichas:
    try:
        balance = Balance.objects.get(laficha)
    except:
        balance = Balance(ficha = laficha, fecha=datetime.now(), capital = laficha.deuda_inicial)
        print balance
        balance.save()
        

    
