# coding=UTF-8
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
import datetime
import time
import re

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Spacer, SimpleDocTemplate, Table, TableStyle
from cStringIO import StringIO


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
                    filtro = filtro|Q(capital=query)

                registro = registro.filter( filtro)

            registro = registro.order_by('fecha','orden')
            data = '({ total: %d, "results": %s })' % \
                (registro.count(),
                 serializers.serialize('json', 
                                       registro, 
                                       indent=4, 
                               relations=({'codigo':{},'forma_pago':{},'receptor':{}})))

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
    sort = request.GET.get('sort',False)
    dir = request.GET.get('dir',False)


    if query:
        query = query.lower()
        #Sacar las palabras clave de la query
        # cerrado e incobrable
        cerrado = False
        incobrable = False
        if 'cerrado' in query:
            cerrado = True
            query = query.replace('cerrado','')

        if 'incobrable' in query:
            incobrable = True
            query = query.replace('incobrable','')
        
        query = query.strip()

        filtro = False
        if query:
            filtro = Q(persona__nombres__icontains=query)
            filtro = filtro|Q(persona__apellidos__icontains=query)
            filtro = filtro|Q(persona__rut__icontains=query)
            filtro = filtro|Q(rol__icontains=query)        
            
        if cerrado:
            if filtro:
                fichas = Ficha.objects.filter(estado='1').filter(filtro)
            else:
                fichas = Ficha.objects.filter(estado='1')

        elif incobrable:
            if filtro:
                fichas = Ficha.objects.filter(estado='2').filter(filtro)
            else:
                fichas = Ficha.objects.filter(estado='2')
        else:
            if filtro:
                fichas = Ficha.objects.filter(estado='0').filter(filtro)
            else:
                fichas = Ficha.objects.filter(estado='0')
    else:
        fichas = Ficha.objects.filter(estado='0')

    if sort == 'fecha':
        sort = 'fecha_creacion'
    if sort == 'nombres':
        sort = 'persona__nombres'
    if sort == 'apellidos':
        sort = 'persona__apellidos'
    if sort == 'rut':
        sort = 'persona__rut'
    if sort == 'procurador_name':
        sort = 'procurador__user__first_name'
    
    if dir == 'DESC':
        sort = '-' + sort

    if sort:
        fichas = fichas.order_by(sort)
    else:
        fichas = fichas.order_by('persona__apellidos')

    #Usando la paginacion

    start = int(request.GET.get('start',0))
    limit = int(request.GET.get('limit',25))
    
    limit += start

    data = '({ total: %d, "results": %s })' % \
        (fichas.count(),
         serializers.serialize('json', 
                               fichas[start:limit], 
                               indent=4, 
                               extras=('getNombreCreador','getNombreProcurador','getRutDeudor','getIdProcurador',),
                               relations=({'procurador':{},'tribunal':{},'persona':{},'creado_por':{}})))


    return HttpResponse(data, content_type='application/json')
    


def getCodigo(request):

    #llenado de lista de codigo
    codigos = Codigo.objects.all()

    if request.user.usuario_set.count() > 0:
        #Si es procurador
        usuario = request.user.usuario_set.get()
        if usuario.get_perfil_display() == 'procurador':
            codigos = Codigo.objects.filter(~Q(descripcion = 'CERRAR FICHA'))


        
    codigos = codigos.order_by('codigo_id')
    data = '({ total: %d, "results": %s })' % \
        (codigos.count(),
         serializers.serialize('json', 
                               codigos,
                               indent=4))

    return HttpResponse(data, content_type='application/json')
    


def getFormaPago(request):
    
    data = '({ total: %d, "results": %s })' % \
        (FormaPago.objects.count(),
         serializers.serialize('json', 
                               FormaPago.objects.all(), 
                               indent=4))

    return HttpResponse(data, content_type='application/json')

    

def getReceptor(request):
    
    data = '({ total: %d, "results": %s })' % \
        (Receptor.objects.count(),
         serializers.serialize('json', 
                               Receptor.objects.all(), 
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

def getSistOrigen(request):
    """ Devuelve la lista de los sistemas
    de origenes en donde proviene la Data """

    data = '({ total: %d, "results": %s })' % \
        (SistemaOrigen.objects.count(),
         serializers.serialize('json', 
                               SistemaOrigen.objects.all(), 
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
    
    ficha = evento.ficha
    campo_modificado = ""

    if campo == 'fecha':
        evento.fecha = datetime.datetime(*time.strptime(valor,
                                                        '%Y-%m-%dT00:00:00')[0:3])
        campo_modificado = 'fecha'

    if campo == 'prox_pago':
        evento.proximo_pago = datetime.datetime(*time.strptime(valor,
                                                        '%Y-%m-%dT00:00:00')[0:3])
        campo_modificado = 'proximo pago'

    if campo == 'orden':
        evento.orden = valor
        campo_modificado = "orden"

    if campo=='codigo':
        codigo = Codigo.objects.get(codigo_id=valor)
        evento.codigo = codigo
        campo_modificado = "codigo"

    if campo == 'descripcion':
        evento.descripcion = valor
        campo_modificado = "Descripcion"
    
    if campo == 'receptor':
        receptor = Receptor.objects.get(id=valor)
        evento.receptor = receptor
        campo_modificado = "Receptor"

    if campo == 'pago':
        pago = FormaPago.objects.get(codigo=valor)
        evento.forma_pago = pago
        campo_modificado = "Forma de Pago"

    if campo == 'capital':
        evento.capital = valor
        campo_modificado ="Capital"

    if campo == 'honorario':
        evento.honorario = valor
        campo_modificado ="Honorario"

    if campo == 'gasto':
        evento.gasto_judicial = valor
        campo_modificado ="Gasto"
        
    if campo == 'tribunal':
        tribunal = Tribunal.objects.get(nombre=valor)
        ficha.tribunal = tribunal
        campo_modificado = "Tribunal"

    if campo == "costas":
        evento.costas = valor
        campo_modificado = "Costas"

    if campo == "interes":
        evento.interes = valor
        campo_modificado = "Interes"

    evento_mod = evento.save()


    #Agregar en bitacora la creacion del nuevo evento
    users = Usuario.objects.filter(user=request.user)
    usuario = None
    if users.count() > 0:
        usuario = users[0]
        
    cambio = Cambio(descripcion="cambio en " + campo_modificado,
                    fecha = datetime.datetime.now(),
                    ficha = ficha,
                    usuario = usuario)
    

    cambio.save()
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
                
            evento = event.save()

            #Agregar en bitacora la creacion del nuevo evento
            users = Usuario.objects.filter(user=request.user)
            usuario = None
            if users.count() > 0:
                usuario = users[0]
                
            cambio = Cambio(descripcion="Creacion del evento",
                            fecha = datetime.datetime.now(),
                            usuario = usuario,
                            ficha = ficha)
            cambio.save()

            #Si el codigo fue "CERRAR FICHA", entonces 
            # se procede a cerrar la ficha
            if codigo.descripcion == 'CERRAR FICHA':
                ficha.estado = '1'
                ficha.save()
            
            #Si el codigo fue "INCOBRABLE", entonces
            # se procede a setear ese campo
            if codigo.descripcion == 'INCOBRABLE':
                ficha.estado = '2'
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
    fecha_creacion = forms.DateField(input_formats=['%d/%m/%Y'],
                                     required=False,
                                     error_messages={'invalid': 'Fecha invalida',
                                                     'required':'Campo Obligatorio'})


    class Meta:
        model = Ficha
        exclude = ('persona','creado_por',
                   'tribunal','procurador', 'estado')
        
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


        ficha_form = FichaForm(request.POST)

        if ficha_form.is_valid():
            ficha = ficha_form.save(commit=False)
        else:
             data = '({ "success": false, "descripcion": %s })' % \
                (ficha_form.errors)

             return HttpResponse(data, 
                                 content_type='application/json')

        ficha.persona = persona

        #Creado por usuario logeado
        if request.user.usuario_set.count():
            ficha.creado_por = request.user.usuario_set.get()

        #busqueda del procurador
        rut_procurador = request.POST.get('proc_rut',False)        
        if rut_procurador:
            procurador = Usuario.objects.get(id = rut_procurador)
            ficha.procurador = procurador

        #busqueda del tribunal
        nombre_tribunal = request.POST.get('trib',False)
        if nombre_tribunal:
            tribunal = Tribunal.objects.get(nombre=nombre_tribunal)

            ficha.tribunal = tribunal

        
        ficha.save()
        
        return HttpResponse()


def updateDeudor(request):
    if request.method == "POST":
        rut = request.POST.get('rut',False)

        #Busqueda de persona por rut
        pers = None
        if rut:
            pers = Persona.objects.filter(rut=rut.split('-')[0].replace('.',''))
            pers = pers[0]
            
        persona_form = PersonaForm(request.POST,
                                   instance=pers)

        if persona_form.is_valid():
            persona = persona_form.save()
        else:            
            data = '({ "success": false, "descripcion": Error en Persona %s })' % \
                (persona_form.errors)

            return HttpResponse(data,
                                content_type='application/json')


        #Recuperar la ficha del deudor

        if persona.ficha_set.count() > 0:
            #Se obtiene la primera ficha. deberia tener solo una

            ficha = persona.ficha_set.all()[0]
            ficha_form = FichaForm(request.POST, 
                                   instance=ficha)
        else:
            ficha_form = FichaForm(request.POST,{'fecha_creacion':request.POST['fecha']})

        if ficha_form.is_valid():
            ficha = ficha_form.save(commit=False)
        else:
             data = '({ "success": false, "descripcion": %s })' % \
                (ficha_form.errors)

             return HttpResponse(data, 
                                 content_type='application/json')

        ficha.fecha_creacion = datetime.datetime(*time.strptime(request.POST['fecha'],'%d/%m/%Y')[0:3])

        #busqueda del procurador
        rut_procurador = request.POST.get('proc_rut',False)
        if rut_procurador:
            procurador = Usuario.objects.get(id = rut_procurador)
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
        
        #Imprimir el header del SQL
        cell_id = 0
        for desc in cur.cursor.description:
            ws0.write(0,cell_id,"%s" % desc[0], font_style)
            cell_id += 1
            
        row_id = 1
        for row in rows:
            cell_id = 0
            for cell in row:
                if cell == None:
                    cell = ''
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
        persona = ficha.persona
        ficha.delete()
        persona.delete()
    return HttpResponse()




def loadData(line):
    """ Carga Datos al model Django
    Returns:
        'persona' Si una nueva persona fue creada
        'ficha' Si una nueva ficha fue creada
        'persona ficha' para ambas
    """

    row = line.split(',')

    apellidos =  row[1].lower()
    nombres = row[2].lower()

    rut = row[0]
    direccion = row[3].lower()

    telefono = row[4]
    celular = row[5]

    deuda = row[6]

    vencimiento = ""
    
    fecha_creacion = datetime.datetime(*time.strptime(row[8],'%Y%m%d')[0:3])

    try:
        vencimiento = datetime.datetime(*time.strptime(row[7],'%Y%m%d')[0:3])
    except:
        pass

    salida = ''
    
    #Buscar en Persona por el rut
    pers_bus = Persona.objects.filter(rut=rut)
    persona = Persona()
    if pers_bus.count() == 0:
        #No existe la persona
        persona.rut = rut
        persona.apellidos = apellidos
        persona.nombres = nombres
        persona.domicilio = direccion
        persona.telefono_fijo = telefono
        persona.telefono_movil= celular

        persona.save()
        salida = 'persona '
    else:
        #existe la persona, obtener el objeto
        persona = pers_bus[0]
        #Ademas ver si es posible actualizar los datos
        #nombres y apellidos:
        actualizar = False
        if nombres != persona.nombres:
            persona.nombres = nombres
            actualizar = True
        if apellidos != persona.apellidos:
            persona.apellidos = apellidos
            actualizar = True
        if actualizar:
            persona.save()
            salida = 'persona actualizada '
            

    #buscar si existe ficha persona
    if persona.ficha_set.count() == 0:
        ficha = Ficha()
        ficha.persona = persona
        ficha.deuda_inicial = deuda
        ficha.fecha_creacion = fecha_creacion
        ficha.save()
        salida += 'ficha'
    else:
        #Si existe ficha, ver si se puede actualizar la fecha
        # de creacion
        ficha = persona.ficha_set.get()
        if ficha.fecha_creacion != fecha_creacion:
            ficha.fecha_creacion = fecha_creacion
            ficha.save()
            salida += "ficha actualizada"
    
    return salida.strip()

@login_needed    
def cargarDatos(request):
    """ Desde un archivo carga los datos de ficha al sistema """
    if request.method == 'POST':
        file = request.FILES['filename']
        data = csv.reader(file,delimiter=';')
        lines = ""
        for row in data:
            #Ver si el nombre viene con 
            # Apellidos - Nombres o al reves
            apellidos = ''
            nombres = ''
            d_nombres = row[2].decode('latin1').encode('utf8')
            nombres_apellidos = \
                [  a for a in  d_nombres.split(" ") if a!= ""]

            if (int(row[1].strip()[:-1]) == int(row[0].strip()[:-2])):
                #Entonces la data es apellidos-nombres
                apellidos =  " ".join(nombres_apellidos[0:2]) 
                nombres = " ".join(nombres_apellidos[2:])

            else:
                #La data viene nombre-apellidos
                apellidos =  " ".join(nombres_apellidos[1:]) 
                nombres = " ".join(nombres_apellidos[:-2])
                
            rut = int(row[1].strip()[:-1])

            direccion = "%s %s %s %s " % (row[4].decode('latin1').encode('utf8').strip().replace(",",""), row[6].decode('latin1').encode('utf8').strip().replace(",",""), row[5].decode('latin1').encode('utf8').strip().replace(",",""), row[7].decode('latin1').encode('utf8').strip().replace(",",""))

            telefono = ""
            if row[9].strip() != "":
                telefono = row[8][4:]+"-"+row[9].strip()

            celular = row[16].strip()

            deuda = int(row[17])
            deuda_int = int(row[18])

            vencimiento = int(row[20])

            fecha = row[22]
            
    
            line = "%s,%s,%s,%s,%s,%s,%s,%s,%s" % (rut, apellidos, nombres, direccion, telefono, celular, deuda_int, vencimiento, fecha)

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
            lines += "<br>" + line

        return HttpResponse(lines)

    else:

        t = loader.get_template('carga_datos.html')
        c = Context({
                'usuario': request.user, })
        return HttpResponse(t.render(c))
    
@login_needed
def printFicha(request):
    """ Dado un id de ficha, se imprime
    en un HTML con la descripcion de la 
    ficha y sus eventos"""

    ficha_id = request.GET.get('ficha_id',False)
    if ficha_id:
        ficha = Ficha.objects.get(id=ficha_id)


        t = loader.get_template('imprimir_ficha.html')
        c = Context({
                'ficha': ficha})

        return HttpResponse(t.render(c))
    else:
        
        data = '({ "success": false, "descripcion": "No hay ficha solicitada"})' 
        return HttpResponse(data, content_type='application/json')


    

def imprimir(request):
    """
    Recibe el rut del deudor e imprime la ficha con 
    sus eventos

    """
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import *
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.pagesizes import A4, LETTER, landscape, portrait 

    rut_deudor = request.GET.get('rut_deudor',False)

    if rut_deudor is False:
        return HttpResponse()
    
    persona = Persona.objects.get(rut=rut_deudor)
    ficha = False
    if persona.ficha_set.count() > 0:
        ficha = persona.ficha_set.get()
    
    eventos = False
    if ficha.evento_set.count() > 0:
        eventos = ficha.evento_set.all().order_by('fecha','orden')

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + rut_deudor + '.pdf'
        

    #Ahora se comienza a escribir el doc

    # Our container for 'Flowable' objects
    elements = []

    # A large collection of style sheets pre-made for us
    styles = getSampleStyleSheet()
    
    style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica-Bold',
        fontSize=9,
        )

    buffer = StringIO()
    doc = SimpleDocTemplate(response)

    #elements.append(Paragraph("Detalle Ficha " + persona.nombres + " " + persona.apellidos,
    #                          styles['Title']))

    #elements.append(Paragraph("Nombres: " + persona.nombres + " " + persona.apellidos, style))
    #elements.append(Spacer(1, 0.2 * inch))
    #elements.append(Paragraph("Rut: " + persona.get_rut(), style))
    #elements.append(Spacer(1, 0.2 * inch))

    rol = "Sin información"
    if ficha.rol:
        rol = ficha.rol
    #elements.append(Paragraph("Rol: " + rol, style))
    #elements.append(Spacer(1, 0.2 * inch))

    carpeta = "Sin información"
    if ficha.carpeta:
        carpeta = ficha.carpeta
    
    #elements.append(Paragraph("Carpeta: " + carpeta, style))
    #elements.append(Spacer(1, 0.2 * inch))

    tribunal = "Sin información"
    if ficha.tribunal:
        tribunal = ficha.tribunal

    #elements.append(Paragraph("Tribunal: " + tribunal, style))
    #elements.append(Spacer(1, 0.2 * inch))

    #creado_por = "Sin información"
    #if ficha.creado_por:
    #    creado_por = ficha.creado_por
    ##elements.append(Paragraph("Creado por: "+ creado_por, style))
    ##elements.append(Spacer(1, 0.2 * inch))

    #elements.append(Paragraph("Fecha creacion: "+ ficha.fecha_creacion.strftime('%d/%m/%Y'), style))
    #elements.append(Spacer(1, 0.2 * inch))

    #elements.append(Paragraph("Deuda Inicial: $"+str(ficha.deuda_inicial), style))
    #elements.append(Spacer(1, 0.2 * inch))

    procurador = "Sin información"
    if ficha.procurador:
        procurador = ficha.procurador

    deuda_inicial = 0
    if ficha.deuda_inicial:
        deuda_inicial = ficha.deuda_inicial 

    estado = "Sin informacion"
    if ficha.estado :
        estado= ficha.get_estado_display()

    ##elements.append(Paragraph("Procurador: "+ procurador, style))
    ##elements.append(Spacer(1, 0.2 * inch))

    ##elements.append(Paragraph("Estado: "+ficha.get_estado_display(), style))
    ##elements.append(Spacer(1, 0.2 * inch))



    desc_style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica',
        fontSize=9,
        )


    header = [['Nombre:',persona.nombres + " " + persona.apellidos, 'Rut:', persona.get_rut()]]
    header.append(['Dirección:',persona.domicilio,'',''])
    header.append(['Teléfono:', persona.telefono_fijo, 'Celular:', persona.telefono_movil ])
    header.append(['Rol:', rol, 'Carpeta:', carpeta ])
    header.append(['Tribunal:', tribunal,'Fecha Asignación:', ficha.fecha_creacion.strftime('%d/%m/%Y')])
    header.append(['Deuda Inicial:', deuda_inicial,'Estado:',estado ])
    
    ts = [
        ('BOX',(0,0),(-1,-1),1,colors.grey),
        ('ALIGN', (1,1), (-1,-1), 'LEFT'),
        ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
        ('FONT', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONT', (1,0), (1,-1), 'Helvetica'),
        ('FONT', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONT', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONT', (3,0), (3,-1), 'Helvetica'),
        ('SPAN', (1,1), (-1,1))]


    head_table = Table(header,[1.2*inch, 2.8*inch, 1.8*inch, 2.8*inch] )
    head_table.setStyle(ts)
    elements.append(head_table)
    elements.append(Spacer(1, 0.2 * inch))        
    data = [['Fecha','Código','Descripción','Receptor']]

    if eventos:
        for evento in eventos:
            codigo = ''
            if evento.codigo.descripcion:
                codigo = evento.codigo.descripcion

            descripcion = ''
            if evento.descripcion:
                descripcion = evento.descripcion
            receptor = ''
            if evento.receptor:
                receptor = evento.receptor
            data.append([Paragraph(evento.fecha.strftime('%d/%m/%Y'), desc_style),Paragraph(codigo, desc_style),Paragraph(descripcion, desc_style), receptor])


    ts2 = [
        ('BACKGROUND',(0,0),(-1,0),colors.grey),
        #('BOX',(0,0),(-1,-1),2,colors.grey),
        ('VALIGN',(0,0),(-1,-1), 'TOP'),
        #('ALIGN', (1,1), (-1,-1), 'LEFT'),
        #('LINEABOVE', (0,0), (0,-1), 1, colors.grey),
        ('FONT', (0,1), (-1,-1), 'Helvetica'),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),[ '#f7f7f7','#f0f0f0',])]

    # The bottom row has one line above, and three lines below of
    # various colors and spacing.
    #    ('FONT', (0,-1), (-1,-1), 'Times-Bold')]

    # Create the table with the necessary style, and add it to the
    # elements list.
    table = Table(data,  style=ts2)
    table._argW[0]=0.8*inch
    table._argW[1]=3*inch
    table._argW[2]=4*inch
    table._argW[3]=0.9*inch
    elements.append(table)
    elements.append(Spacer(1, 0.2 * inch))
    
    # Write the document to disk
    doc.pagesize = landscape(LETTER)
    doc.build(elements) 
    response.write(buffer.getvalue())
    buffer.close()
    return response
    
