# coding=UTF-8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

from settings import TASA_INTERES

PERFIL_USUARIO = (
    ('0','administrador'),
    ('1','cobranza'),
    ('2','procurador'))


class Persona(models.Model):
    nombres = models.CharField(max_length=80, blank=True, null=True)
    apellidos = models.CharField(max_length=80)
    rut = models.IntegerField(primary_key=True )
    domicilio = models.CharField(max_length=150, null=True, blank = True)
    comuna = models.CharField(max_length=100, null=True, blank = True)
    ciudad = models.CharField(max_length=100, null=True, blank = True)
    profesion = models.CharField(max_length=100, null=True, blank = True)
    telefono_fijo = models.CharField(max_length=12, null=True , blank=True)
    telefono_oficina = models.CharField(max_length=12, null=True, blank=True)
    telefono_movil = models.CharField(max_length=12, null=True, blank=True)
    correo = models.EmailField(blank=True,null=True)

    def __unicode__(self):
        return u"%s %s" % (self.nombres, self.apellidos)

    def short_name(self):
        return u"%s %s" % (self.nombres.split(" ")[0], 
                           self.apellidos.split(" ")[0])

    def get_digito_verificador(self):
        """
        Entrega el digito verificador de self.rut
        """
        if self.rut is None:
            return ''
        s=1
        m=0
        rut = int(self.rut)
        while(rut != 0):
            s = (s + rut % 10 * (9 - m % 6) ) % 11
            m += 1
            rut /= 10
        if s:
            return s-1
        else:
            return 'k'

    def get_rut(self):
        """
        Devuelve el rut con digito verificador
        """
        return  str(self.rut) + '-' + str(self.get_digito_verificador())

class Usuario(models.Model):
    user = models.ForeignKey(User)
    perfil = models.CharField(max_length=1,choices=PERFIL_USUARIO)

    def __unicode__(self):
        return self.user.__unicode__()

    def short_name(self):
        return self.user.get_full_name()

class Codigo(models.Model):
    codigo_id = models.IntegerField(primary_key=True)
    descripcion = models.TextField(max_length=200)
    
    def __unicode__(self):
        return self.descripcion

class Tribunal(models.Model):
    nombre = models.CharField(max_length=100)
    nombre_juez = models.CharField(max_length=50, blank=True, null=True)
    direccion = models.CharField(max_length=50, blank=True, null=True)
    ciudad = models.CharField(max_length=50)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    fax = models.CharField(max_length=12, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    web = models.URLField(verify_exists=False, blank=True, null=True)
    secretario = models.CharField(max_length=50, blank=True, null=True)
    direccion_secretario = models.CharField(max_length=50,blank=True, null=True)
  
    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = 'tribunales'

class SistemaOrigen(models.Model):
    nombre = models.TextField(max_length=100)
    
    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Sistemas de Origen"

ESTADOS = (
    ('0','activo'),
    ('1','cerrado'),
    ('2','incobrable'))

class Ficha(models.Model):
    persona = models.ForeignKey(Persona)
    rol = models.TextField(max_length=100, blank=True, null=True)
    carpeta = models.TextField(max_length=50, blank=True, null=True)
    tribunal = models.ForeignKey(Tribunal , blank=True, null=True)

    creado_por = models.ForeignKey(Usuario, related_name='usuario_set',blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)


    deuda_inicial = models.IntegerField(blank=True, null=True)
    procurador = models.ForeignKey(Usuario, blank=True, null=True)

    estado = models.CharField(max_length=1,choices=ESTADOS, default='0')
    sistema_origen = models.ForeignKey(SistemaOrigen, blank=True, null=True)

    interes = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        if self.rol:
            return self.rol
        else:
            return self.persona.__unicode__()
    

    def getNombreCreador(self):
        if self.creado_por:
            return self.creado_por.short_name()
        else:
            return ''

    def getNombreProcurador(self):
        if self.procurador:
            return self.procurador.short_name()
        else:
            return ''

    def getIdProcurador(self):
        if self.procurador:
            return self.procurador.id
        else:
            return ''

    def getRutDeudor(self):
        """ Devuelve el rut con digito verificador
        del deudor 
        """
        if self.persona:
            return self.persona.get_rut()
        else:
            return ''

    def getCapitalPagado(self):
        """ Devuelve la suma de todos los capitales pagados
        de los eventos de la ficha
        """
        abonos = 0
        for evento in self.evento_set.all():
            if evento.capital:
                abonos += evento.capital

        return abonos

    def getCapitalFaltante(self):
        """ Devuelve el dinero faltante para
        pagar la deuda inicial 
        """
        return self.deuda_inicial - self.getCapitalPagado()

    def estaCapitalPagado(self):
        """ Devuelve True si la suma de los capitales
        pagados de los eventos de la ficha son iguales
        a la deuda inicial de la ficha
        """
        abono = self.getCapitalPagado()
        if abono == self.deuda_inicial:
            return True
        else:
            return False


    def getGastoJudicial(self):
        """ Devuelve la suma de los gastos judiciales
        de cada evento
        """
        gasto = 0
        for evento in self.evento_set.all():
            if evento.gasto_judicial != None:
                gasto += evento.gasto_judicial
        return gasto

    def getCostasTotal(self):
        """ Devuelve la suma de las costas de 
        cada evento """
        costa = 0
        for evento in self.evento_set.all():
            if evento.costas != None:
                costa += evento.costas
        return costa


    def estaGastoJudicialPagado(self):
        """ Devuelve True si la suma de los 
        gastos judiciales son iguales a las costas"""

        gastos = self.getGastoJudicial()
        costas = self.getCostasTotal()
        if gastos == costas:
            return True
        else:
            return False

    def getGastoJudicialFaltante(self):
        """ Devuelve el valor de gastos judiciales
        faltante para saldarlos """

        gastos = self.getGastoJudicial()
        costas = self.getCostasTotal()
        if gastos > costas:
            return gastos - costas
        else:
            return 0

    def getPrimerPago(self):
        """ Devuelve el evento donde se realizo 
        el primer pago """
        
        for evento in self.evento_set.all().order_by('fecha'):
            if (evento.codigo_id == 143 or \
                    evento.codigo_id == 148):
                return evento
            
    def getInteres(self, fecha_inicio=None, fecha_fin=None):
        """ 
        Calcula el interes automaticamente tomando
        las fechas de asignacion y primer pago
        
        Si las fechas por argumento son distintas a None, 
        entonces se utilizan esas fechas para el calculo de
        interes

        Return None si no tiene fecha de creacion

        """
        
        if not self.fecha_creacion:
            return None

        dias = 1
        if fecha_inicio == None or fecha_fin == None:
            fecha_primer_pago = self.getPrimerPago().fecha
            dias = (fecha_primer_pago - self.fecha_creacion).days

        else:
            dias = (fecha_fin - fecha_inicio).days
            
        return self.deuda_inicial * dias * TASA_INTERES/100


    def estaInteresPagado(self):
        """ Devuelve True si se han pagado la totalidad
        de los intereses """
        
        interes_pagado = 0
        for evento in self.evento_set.all().order_by('fecha'):
            if evento.interes != None:
                interes_pagado += evento.interes
            
        if interes_pagado >= self.interes:
            return True
        else:
            return False


    def getInteresPagado(self):
        """ Devuelve la suma de los intereses pagados"""

        interes_pagado = 0
        for evento in self.evento_set.all().order_by('fecha'):
            interes_pagado = evento.interes

        return interes_pagado


    def getInteresFaltante(self):
        """ Devuelve el interes faltante
        para cancelar el monto total """
        
        interes_pagado = self.getInteresPagado()

        if self.interes > interes_pagado:
            return self.interes - interes_pagado
        else:
            return 0
        
    def setInteres(self, interes = None):
        """
        Setea el interes de una ficha.
        Si no ingresan interes, entonces lo calcula
        a partir del primer pago
        """
        if interes:
            self.interes = interes
        else:
            self.interes = self.getInteres()
            
        self.save()

class FormaPago(models.Model):
    codigo = models.IntegerField()
    nombre = models.TextField(max_length=50)


    def __unicode__(self):
        return self.nombre

class Receptor(models.Model):
    nombre = models.TextField(max_length=200)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Receptores"

class Evento(models.Model):
    ficha = models.ForeignKey(Ficha)
    fecha = models.DateTimeField()
    orden = models.IntegerField(blank=True, null=True)
    proximo_pago = models.DateTimeField(blank=True, null=True)

    codigo = models.ForeignKey(Codigo)
    
    descripcion =  models.TextField(max_length=200, blank=True, null=True)

    forma_pago = models.ForeignKey(FormaPago, blank=True, null=True)
    capital = models.IntegerField(blank=True, null=True)

    gasto_judicial = models.IntegerField(blank=True, null=True)
    honorario = models.IntegerField(blank=True, null=True)
    interes = models.IntegerField(blank=True, null=True)
    costas = models.IntegerField(blank=True, null=True)

    receptor = models.ForeignKey(Receptor, blank=True, null=True)

    def __unicode__(self):
        return self.descripcion


class Cambio(models.Model):

    ficha = models.ForeignKey(Ficha,blank=True, null=True)
    usuario = models.ForeignKey(Usuario, blank= True, null=True)
    descripcion = models.TextField(max_length=500, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)


class Reporte(models.Model):
    nombre = models.TextField(max_length=50)
    sql = models.TextField(max_length=1000)

    def __unicode__(self):
        return self.nombre
