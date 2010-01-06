from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.template import Context, loader

from django.core import serializers

from django import forms
from django.db.models import Q
from django.db import connection

from core.models import *

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
        rut = request.GET.get('rut',False)
        if rut:
            #Busqueda de persona
            persona = Persona.objects.filter(rut=rut)
            #Solo si se encontro la persona
            if persona.count() <= 0:
                return HttpResponse('({"total":0,'\
                            '"results":False})',  mimetype="text/plain", content_type="application/json")
                
            #@TODO: Solo tomara la primera persona que calce con rut,
            # Que pasa si existe mas de una persona con mismo rut?
            # Debiese el sistema permitir esto?
            persona = persona[0]
            #Buscar ficha y luego eventos
            ficha = Ficha.objects.filter(persona=persona)
            if ficha.count() == 0:
                return HttpResponse('({"total":0,'\
                            '"results":False})',  mimetype="text/plain", content_type="application/json")
            
            ficha = ficha[0]
            registro = Evento.objects.filter(ficha=ficha)

            #Ver si es que fueron enviados datos para el filtrado
            # de eventos

            query = request.GET.get('query',False)
            if query:
                filtro = Q(descripcion__icontains=query)
                filtro = filtro|Q(codigo__descripcion__icontains=query)

                # Si la query es numero entonces puede 
                # ser que quieran filtrar por codigo
                if query.isdigit():
                    filtro = filtro|Q(abono_deuda=query)

                registro = registro.filter( filtro)


            data = '({ total: %d, "results": %s })' % \
                (registro.count(),
                 serializers.serialize('json', 
                                       registro, 
                                       indent=4, 
                               relations=({'codigo':{}})))

            return HttpResponse(data, content_type='application/json')



        else:
            return HttpResponse('({"total":0,'\
                            '"results":[]})',  mimetype="text/plain", content_type="application/json")


def getFicha(request):
    
    query = request.GET.get('query',False)
    

    if query:
        filtro = Q(persona__nombres__icontains=query)
        filtro = filtro|Q(persona__apellidos__icontains=query)
        filtro = filtro|Q(persona__rut__icontains=query)
        filtro = filtro|Q(rol__icontains=query)        
        fichas = Ficha.objects.filter(filtro)
    else:
        fichas = Ficha.objects.all()

    data = '({ total: %d, "results": %s })' % \
        (fichas.count(),
         serializers.serialize('json', 
                               fichas, 
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
        
        
class EventoForm(forms.ModelForm):
    fecha = forms.DateField(input_formats=['%d/%m/%Y'],error_messages={'invalid': 'Fecha invalida','required':'Campo Obligatorio'})

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
            
            return HttpResponse(event_form.errors)
        

class PersonaForm(forms.ModelForm):
    rut  = forms.CharField(required=False)

    class Meta:
        model = Persona

    def clean_rut(self):
        rut = self.cleaned_data['rut']

        #Sacar el digito verificador
        if len(rut.split('-')) == 2:
            rut = rut.split('-')[0]
        rut = rut.replace('.','')

        return int(rut)
        

class FichaForm(forms.ModelForm):
    fecha_creacion = forms.DateField(input_formats=['%d/%m/%Y'],error_messages={'invalid': 'Fecha invalida','required':'Campo Obligatorio'})


    class Meta:
        model = Ficha
        exclude = ('persona','creado_por','tribunal','procurador')
        
def putDeudor(request):

    if request.method == "POST":

        persona_form = PersonaForm(request.POST)
        if persona_form.is_valid():
            persona = persona_form.save()
        else:
            return HttpResponse(persona_form.errors)


        #busqueda del tribunal
        tribunal = Tribunal.objects.get(nombre=request.POST['trib'])

        #busqueda del procurador
        procurador = Usuario.objects.get(persona__rut = request.POST['proc_rut'])

        ficha_form = FichaForm(request.POST)
        if ficha_form.is_valid():
            ficha = ficha_form.save(commit=False)
        else:
            return HttpResponse(ficha_form.errors)

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