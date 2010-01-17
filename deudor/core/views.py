from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.template import Context, loader

from django.core import serializers

from django import forms
from django.db.models import Q
from django.db import connection
from django.contrib.auth.models import User

from core.models import *

import pyExcelerator
import tempfile
import csv

login_needed = user_passes_test(lambda u: not u.is_anonymous(), login_url='/deudor/login/')
procurador_needed = user_passes_test(lambda u: not u.is_anonymous() and u.usuario_set.get() and u.usuario_set.get().get_perfil_display() == 'procurador', login_url='/deudor/login/')
procurador_needed = user_passes_test(lambda u: not u.is_anonymous() and u.usuario_set.get() and u.usuario_set.get().get_perfil_display() == 'procurador', login_url='/deudor/login/')
cobranza_needed = user_passes_test(lambda u: not u.is_anonymous() and u.usuario_set.get() and u.usuario_set.get().get_perfil_display() == 'cobranza', login_url='/deudor/login/')
administrador_needed = user_passes_test(lambda u: not u.is_anonymous() and u.usuario_set.get() and u.usuario_set.get().get_perfil_display() == 'administrador', login_url='/deudor/login/')


  
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



@login_needed
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
                               relations=({'codigo':{},'forma_pago':{}})))

            return HttpResponse(data, content_type='application/json')



        else:
            return HttpResponse('({"total":0,'\
                            '"results":[]})',  mimetype="text/plain", content_type="application/json")


def getDeudor(request):
    """ obtiene una pesona a travez del rut"""

    rut = request.GET.get('rut',False)
    if rut:
        persona = Persona.objects.get(rut=rut)
        if persona:
            data = '({ total: %d, "results": %s })' % \
                (1,
                 serializers.serialize('json', 
                                       persona, 
                                       indent=4, 
                               ))

            return HttpResponse(data, 
                                content_type='application/json')
    return HttpResponse('({"resultado":"no existe"})')
            
        

def getFicha(request):
    
    query = request.GET.get('query',False)
    

    if query:
        filtro = Q(persona__nombres__icontains=query)
        filtro = filtro|Q(persona__apellidos__icontains=query)
        filtro = filtro|Q(persona__rut__icontains=query)
        filtro = filtro|Q(rol__icontains=query)        
        fichas = Ficha.objects.filter(esta_cerrado=False).filter(filtro)
    else:
        fichas = Ficha.objects.filter(esta_cerrado=False).order_by('persona__apellidos')

    data = '({ total: %d, "results": %s })' % \
        (fichas.count(),
         serializers.serialize('json', 
                               fichas, 
                               indent=4, 
                               extras=('getNombreCreador','getNombreProcurador',),
                               relations=({'procurador':{},'tribunal':{},'persona':{},'creado_por':{}})))

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

    procuradores = Usuario.objects.filter(perfil = '2')

    data = '({ total: %d, "results": %s })' % \
        (procuradores.count(),
         serializers.serialize('json', 
                               procuradores, 
                               extras=('short_name',),
                               indent=4))

    return HttpResponse(data, content_type='application/json')

def getUsuarios(request):
    usuarios = Usuario.objects.all()

    data = '({ total: %d, "results":  %s  })' % \
        (usuarios.count(),
         serializers.serialize('json',
                               usuarios,
                               indent=4,
                               excludes=('perfil'),
                               extras=('short_name',),
                               relations={'user':{'fields':('nombres')}}))

    return HttpResponse(data, content_type='application/json')

    
def getTribunales(request):
    data = '({ total: %d, "results": %s })' % \
        (Tribunal.objects.count(),
         serializers.serialize('json', 
                               Tribunal.objects.all(), 
                               indent=4))

    return HttpResponse(data, content_type='application/json')



def putFicha(request):
    """ Ingreso de una nueva ficha deudor """

    campo = request.POST.get('campo',False)
    id = request.POST.get('id',False)
    valor = request.POST.get('valor',False)

    if valor == "":
        return HttpResponse('{"success":false,"descripcion":"Ingreso vacio"}', 
                            content_type='application/json')
    
        
    try:
        ficha =  Ficha.objects.get(id=id)
    except:
        return HttpResponse('{"success":false,"descripcion":"no encontro ficha"}', 
                            content_type='application/json')
    
    campo_modificado=""
    if campo=='creado_por':
        usuario = Usuario.objects.get(id=valor)
        ficha.creado_por = usuario
        campo_modificado = "Creado_por"

    if campo == 'carpeta':
        ficha.carpeta = valor
        campo_modificado = "Carpeta"
    if campo == 'rol':
        ficha.rol = valor
        campo_modificado ="Rol"

    if campo == 'procurador':
        procurador = Usuario.objects.get(id=valor)
        ficha.procurador = procurador
        campo_modificado = "Procurador"
        
    if campo == 'tribunal':
        tribunal = Tribunal.objects.get(nombre=valor)
        ficha.tribunal = tribunal
        campo_modificado = "Tribunal"


    ficha.save()

    return HttpResponse('{"success":"true","modificaciones":"'+campo_modificado +'" }', 
                        content_type='application/json')


def putEventoEdit(request):

    campo = request.POST.get('campo',False)
    id = request.POST.get('id',False)
    valor = request.POST.get('valor',False)
    rut_deudor = request.POST.get('rut_deudor',False)

    if valor == "":
        return HttpResponse('{"success":"error","descripcion":"Ingreso vacio"}', 
                            content_type='application/json')
    
        
    try:
        evento =  Evento.objects.get(id=id)
    except:
        return HttpResponse('{"result":"error","descripcion":"no se encontro evento "}', 
                            content_type='application/json')
    
    campos_modificados=""
    if campo=='codigo':
        codigo = Codigo.objects.get(codigo_id=valor)
        evento.codigo = codigo
        campo_modificado = "codigo"

    if campo == 'descripcion':
        evento.descripcion = valor
        campo_modificado = "Descripcion"


    if campo == 'pago':
        pago = FormaPago.objects.get(codigo=valor)
        evento.forma_pago = pago
        campo_modificado = "Forma de Pago"

    if campo == 'abono':
        evento.abono = valor
        campo_modificado ="Abono"

    if campo == 'honorario':
        evento.honorario = valor
        campo_modificado ="Honorario"

    if campo == 'gasto':
        evento.gasto = valor
        campo_modificado ="Gasto"
        
    if campo == 'tribunal':
        tribunal = Tribunal.objects.get(nombre=valor)
        ficha.tribunal = tribunal
        campo_modificado = "Tribunal"


    evento.save()

    return HttpResponse('{"result":"success","modificaciones":"'+campo_modificado +'" }', 
                        content_type='application/json')


def buscar(request):

    if request.method == "POST" \
       and 'key' in request.POST.keys():
            
        key = request.POST['key']
        
        #por nombre cliente
        Persona.objects.filter(nombre__icontains=key)
        
        
class EventoForm(forms.ModelForm):
    fecha = forms.DateField(input_formats=['%d/%m/%Y'],
                            error_messages={'invalid': 'Fecha invalida',
                                            'required':'Campo Obligatorio'})

    proximo_pago = forms.DateField(input_formats=['%d/%m/%Y'],
                                   error_messages={'invalid': 'Fecha invalida'}, 
                                   required=False)

    class Meta:
        model = Evento
        exclude = ('ficha','codigo','forma_pago')

def putEvento(request):
    """ Ingreso de un nuevo evento para una ficha """

    if request.method == "POST":
        
        rut_deudor = request.POST.get('rut_deudor',False)
        codigo_id = request.POST.get('codigo',False)

        forma_pago_codigo = request.POST.get('formapago_codigo',False)

        event_form = EventoForm(request.POST)

        if event_form.is_valid() and rut_deudor:

            ficha = Ficha.objects.get(persona__rut = rut_deudor)

            codigo  = Codigo.objects.get(codigo_id = codigo_id)

            event = event_form.save(commit=False)
            event.ficha = ficha
            event.codigo = codigo

            if forma_pago_codigo:
                formapago = FormaPago.objects.get(codigo= forma_pago_codigo)
                event.forma_pago = formapago

            event.save()

            #Si el codigo fue "CERRAR FICHA", entonces 
            # se procede a cerrar la ficha
            if codigo.descripcion == 'CERRAR FICHA':
                ficha.esta_cerrado = True
                ficha.save()
            

            return HttpResponse()

        else:
            
            data = '({ "success": false, "descripcion": %s })' % \
                (event_form.errors)


            return HttpResponse(data, content_type='application/json')


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
        rut = request.POST.get('rut',False)

        #Busqueda de persona por rut
        pers = None
        if rut:
            pers = Persona.objects.filter(rut=rut.split('-')[0].replace('.',''))

        persona_form = PersonaForm(request.POST)

        if persona_form.is_valid():
            persona = persona_form.save()
        else:
            
            #return HttpResponse(str(persona_form.errors))
            data = '({ "success": false, "descripcion": %s })' % \
                (persona_form.errors)


            return HttpResponse(data, content_type='application/json')



            #return HttpResponse('({"success":false, "descripcion":""})',
            #                    content_type='application/json')

        ficha_form = FichaForm(request.POST)
        if ficha_form.is_valid():
            ficha = ficha_form.save(commit=False)
        else:
            return HttpResponse(ficha_form.errors)

        ficha.persona = persona

        #Creado por usuario logeado
        if request.user.usuario_set.count():
            ficha.creado_por = request.user.usuario_set.get()

        #busqueda del procurador
        rut_procurador = request.POST.get('proc_rut',False)        
        if rut_procurador:
            procurador = Usuario.objects.get(persona__rut = rut_procurador)
            ficha.procurador = procurador

        #busqueda del tribunal
        nombre_tribunal = request.POST.get('trib',False)
        if nombre_tribunal:
            tribunal = Tribunal.objects.get(nombre=nombre_tribunal)

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


def getDeudorJs(request):

    t = loader.get_template('js/deudor.js')
    c = Context({
           'usuario': request.user, })
    return HttpResponse(t.render(c))


def deleteEvento(request):
    """ Borra un evento con el id """

    id_evento =  request.GET.get('id', False)
    if id_evento:
        evento = Evento.objects.get(id = id_evento)
        evento.delete()
    
    return HttpResponse()
    

def deleteFicha(request):
    """ Borra una ficha mediante un id """
    id_ficha =  request.GET.get('id', False)
    if id_ficha:
        ficha = Ficha.objects.get(id = id_ficha)
        ficha.delete()
    
    return HttpResponse()
    
    
