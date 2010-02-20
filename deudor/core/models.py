# coding=UTF-8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

PERFIL_USUARIO = (
    ('0','administrador'),
    ('1','cobranza'),
    ('2','procurador'))


class Persona(models.Model):
    nombres = models.CharField(max_length=80)
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

    def __unicode__(self):
        if self.rol:
            return self.rol
        else:
            return self.persona.__unicode__()
    

    def getNombreCreador(self):
        if self.creado_por:
            return self.creado_por.short_name()

    def getNombreProcurador(self):
        if self.procurador:
            return self.procurador.short_name()

class FormaPago(models.Model):
    codigo = models.IntegerField()
    nombre = models.TextField(max_length=50)


    def __unicode__(self):
        return self.nombre

class Receptor(models.Model):
    nombre = models.TextField(max_length=200)

    def __unicode__(self):
        return self.nombre


class Evento(models.Model):
    ficha = models.ForeignKey(Ficha)
    fecha = models.DateTimeField()
    fecha_creacion = models.DateTimeField(blank=True, null=True)
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
