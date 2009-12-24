from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.template import Context, loader

from django.core import serializers
from django.forms import ModelForm

from django.db import connection

from jjdonoso.core.models import *

import pyExcelerator
import tempfile
import csv

login_needed = user_passes_test(lambda u: not u.is_anonymous(), login_url='/jjdonoso/login/')
  


def Serialize(queryset, root_name=None):

    if not root_name:

        root_name = queryset.model._meta.verbose_name_plural

    return '{"total": %s, "%s": %s}' % \
        (queryset.count(), root_name, serializers.serialize('json', queryset))


def main(request):
    
    t = loader.get_template('index.html')
    c = Context({
            })
    return HttpResponse(t.render(c))



def ficha(request):
    
    t = loader.get_template('ficha.html')
    c = Context({
            })
    return HttpResponse(t.render(c))
    


def getEvento(request):

    if request.method == "GET":
        if 'rut' in request.GET.keys():
            #Busqueda de persona
            rut = request.GET['rut']
            persona = Persona.objects.filter(rut=rut)
            #@TODO: Ver si el usuario se encontro
            ficha = Ficha.objects.filter(persona=persona)[0]

            registro = Evento.objects.filter(ficha=ficha)

            data = '({ total: %d, "results": %s })' % \
                (registro.count(),
                 serializers.serialize('json', 
                                       registro, 
                                       indent=4, 
                               relations=({'codigo':{}})))

            return HttpResponse(data, content_type='application/json')


            #return HttpResponse(Serialize(ficha, root_name='fichas'), mimetype='text/javascript', content_type="application/json") 

        


        else:
            return HttpResponse('({"total":3,'\
                            '"results":[{"fecha":"2009/12/01","codigo":"23","descripcion":"empiea la deuda","pago":"contado","abono":"2121","gasto":"121","honorario":"1212"},{"fecha":"2009/11/21","codigo":"13","descripcion":"sigue la deuda","pago":"contado","abono":"55421","gasto":"54545","honorario":"323223"},{"fecha":"2009/11/11","codigo":"66","descripcion":"termina la deuda","pago":"contado","abono":"2121","gasto":"121","honorario":"1212"}]})',  mimetype="text/plain", content_type="application/json")


def getFicha(request):

    

    data = '({ total: %d, "results": %s })' % \
        (Ficha.objects.count(),
         serializers.serialize('json', 
                               Ficha.objects.all(), 
                               indent=4, 
                               relations=({'procurador':{'relations':('persona',)},'tribunal':{},'persona':{},'creado_por':{'relations':('persona',)}})))

    return HttpResponse(data, content_type='application/json')
    


def getCodigo(request):

    data = '({ total: %d, "results": %s })' % \
        (Codigo.objects.count(),
         serializers.serialize('json', 
                               Codigo.objects.all(), 
                               indent=4))

    return HttpResponse(data, content_type='application/json')
    


def getFormaPago(request):
    
    data = '({ total: %d, "results": %s })' % \
        (FormaPago.objects.count(),
         serializers.serialize('json', 
                               FormaPago.objects.all(), 
                               indent=4))

    return HttpResponse(data, content_type='application/json')
    
def getProcuradores(request):

    procuradores = Persona.objects.filter(usuario__perfil = '2')

    data = '({ total: %d, "results": %s })' % \
        (procuradores.count(),
         serializers.serialize('json', 
                               procuradores, 
                               indent=4))

    return HttpResponse(data, content_type='application/json')
    

def getTribunales(request):
    data = '({ total: %d, "results": %s })' % \
        (Tribunal.objects.count(),
         serializers.serialize('json', 
                               Tribunal.objects.all(), 
                               indent=4))

    return HttpResponse(data, content_type='application/json')


def buscar(request):

    if request.method == "POST" \
       and 'key' in request.POST.keys():
            
        key = request.POST['key']
        
        #por nombre cliente
        Persona.objects.filter(nombre__icontains=key)
        
        


def nuevoDeudor(request):
    """" Almacena los datos del deudor """
    if request.method == "POST":
        #toma datos de persona
        nombre = request.POST['nombre']
        rut = request.POST['rut']


class EventoForm(ModelForm):
    class Meta:
        model = Evento
        exclude = ('ficha','codigo','forma_pago')

def putEvento(request):

    if request.method == "POST":
        #return HttpResponse(request.POST.REQUEST)
        #event_form = EventoForm(request.POST)
        
        rut_deudor = request.POST['rut_deudor']
        codigo_id = request.POST['codigo']
        forma_pago_codigo = request.POST['formapago_codigo']

        event_form = EventoForm(request.POST)

        if event_form.is_valid() and rut_deudor:
            ficha = Ficha.objects.get(persona__rut = rut_deudor)

            codigo  = Codigo.objects.get(codigo_id = codigo_id)
            formapago = FormaPago.objects.get(codigo= forma_pago_codigo)

            event = event_form.save(commit=False)
            event.ficha = ficha
            event.codigo = codigo
            event.forma_pago = formapago
            event.save()
            return HttpResponse()

        else:
            
            return HttpResponse("Errores")
        

class PersonaForm(ModelForm):
    class Meta:
        model = Persona

class FichaForm(ModelForm):
    class Meta:
        model = Ficha
        exclude = ('persona','creado_por','tribunal','procurador')
        
def putDeudor(request):

    if request.method == "POST":

        persona_form = PersonaForm(request.POST)
        persona = persona_form.save()
        
        #return HttpResponse(persona.id)

        #busqueda del tribunal
        tribunal = Tribunal.objects.get(nombre=request.POST['trib'])

        #busqueda del procurador
        procurador = Usuario.objects.get(persona__rut = request.POST['proc_rut'])

        ficha_form = FichaForm(request.POST)
        ficha = ficha_form.save(commit=False)

        ficha.persona = persona

        #Arreglar esto de usuarios
        usuario = Usuario.objects.all()[0]
        ficha.creado_por = usuario
        ficha.procurador = procurador
        ficha.tribunal = tribunal
        
        ficha.save()
        
        return HttpResponse()



def getReporte(request):

    if 'nombre' in request.POST.keys():
        
        reporte = Reporte.objects.get(nombre= request.POST['nombre'])

        #conn = psycopg2.connect("dbname='jjdonoso' user='jjdonoso' host='localhost' password='jjdonoso!'");
        cur = connection.cursor()
        
        cur.execute(reporte.sql)

        rows = cur.fetchall()
        
        wb = pyExcelerator.Workbook()
        font = pyExcelerator.Font()
        font.bold = True
        font_style = pyExcelerator.XFStyle()
        font_style.font = font

        ws0 = wb.add_sheet('Reporte')
        
        row_id = 0
        for row in rows:
            cell_id = 0
            for cell in row:
                ws0.write(row_id,cell_id,"%s" % cell,font_style)
                cell_id += 1
            row_id += 1
        
        (fd,path) = tempfile.mkstemp()
        wb.save(path)
        response = HttpResponse(open(path,'r').read())

        response['Content-Type'] = 'application/vnd.ms-excel'
        response['Content-disposition'] = 'Attachment;filename=reporte.xls'
        return response
            
    else:
    
        data = '({ total: %d, "results": %s })' % \
            (Reporte.objects.count(),
             serializers.serialize('json', 
                                   Reporte.objects.all(), 
                                   indent=4))

        return HttpResponse(data, content_type='application/json')


def putReporte(request):


    if request.POST.has_key('sql'):
      
        sql = request.POST['sql']
        conn = psycopg2.connect("dbname='jjdonoso' user='jjdonoso' host='localhost' password='jjdonoso!'");
        cur = conn.cursor()

        
        cur.execute(sql)


        rows = cur.fetchall()

        
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=somefilename.csv'

        writer = csv.writer(response)
        
        for row in rows:
            writer.writerow(row)

        return response

    else:
        return HttpResponse("sin data")
