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
    rut = models.IntegerField(null=True, blank = True)
    domicilio = models.CharField(max_length=150, null=True, blank = True)
    comuna = models.CharField(max_length=100, null=True, blank = True)
    ciudad = models.CharField(max_length=100, null=True, blank = True)
    profesion = models.CharField(max_length=100, null=True, blank = True)
    telefono_fijo = models.CharField(max_length=12, null=True , blank=True)
    telefono_oficina = models.CharField(max_length=12, null=True, blank=True)
    telefono_movil = models.CharField(max_length=12, null=True, blank=True)
    correo = models.EmailField(blank=True,null=True)

    def __unicode__(self):
        return self.nombres.split(' ')[0] + ' ' + self.apellidos

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
    persona = models.ForeignKey(Persona)
    perfil = models.CharField(max_length=1,choices=PERFIL_USUARIO)


class Codigo(models.Model):
    codigo_id = models.TextField(max_length=60)
    descripcion = models.TextField(max_length=200)
    


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
  


class Ficha(models.Model):
    persona = models.ForeignKey(Persona)
    rol = models.TextField(max_length=100)
    carpeta = models.TextField(max_length=50)
    tribunal = models.ForeignKey(Tribunal)

    creado_por = models.ForeignKey(Usuario, related_name='usuario_set')
    fecha_creacion = models.DateTimeField()


    deuda_inicial = models.IntegerField()
    procurador = models.ForeignKey(Usuario)


FORMA_PAGO = (
    ('0','efectivo'),
    ('1','cheque'),
    ('2','deposito'),
    ('3','valevista'))


class Evento(models.Model):
    ficha = models.ForeignKey(Ficha)
    fecha = models.DateTimeField()
    codigo = models.ForeignKey(Codigo)
    
    descripcion =  models.TextField(max_length=200)

    forma_pago = models.CharField(max_length=1,choices=FORMA_PAGO)
    abono_deuda = models.IntegerField()

    gasto_judicial = models.IntegerField()
    honorario = models.IntegerField()
    

