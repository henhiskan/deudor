# coding=UTF-8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from datetime import datetime

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
#        return u"%s %s" % (self.nombres, self.apellidos)
        return self.get_rut()


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
    rol = models.TextField(max_length=15, blank=True, null=True)
    carpeta = models.TextField(max_length=15, blank=True, null=True)
    tribunal = models.ForeignKey(Tribunal , blank=True, null=True)

    creado_por = models.ForeignKey(Usuario, related_name='usuario_set',blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    deuda_inicial = models.IntegerField(blank=True, null=True)
    procurador = models.ForeignKey(Usuario, blank=True, null=True)

    estado = models.CharField(max_length=1,choices=ESTADOS, default='0')
    sistema_origen = models.ForeignKey(SistemaOrigen, blank=True, null=True)

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

#---------------------------------------------------------------------------
class Evento(models.Model):
    ficha = models.ForeignKey(Ficha)
    fecha = models.DateTimeField()
    orden = models.IntegerField(blank=True, null=True)
    proximo_pago = models.DateTimeField(blank=True, null=True)

    codigo = models.ForeignKey(Codigo)
    
    descripcion =  models.TextField(max_length=200, blank=True, null=True)

    forma_pago = models.ForeignKey(FormaPago, blank=True, null=True)
    capital = models.IntegerField(blank=True, null=True)

    abono = models.IntegerField(blank=True, null=True)
    gasto_judicial = models.IntegerField(blank=True, null=True)
    honorario = models.IntegerField(blank=True, null=True)
    interes = models.IntegerField(blank=True, null=True)
    costas = models.IntegerField(blank=True, null=True)

    receptor = models.ForeignKey(Receptor, blank=True, null=True)

    def __unicode__(self):
        return self.descripcion


#---------------------------------------------------------------------------

class Cambio(models.Model):

    ficha = models.ForeignKey(Ficha,blank=True, null=True)
    usuario = models.ForeignKey(Usuario, blank= True, null=True)
    descripcion = models.TextField(max_length=500, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

#---------------------------------------------------------------------------
class Reporte(models.Model):
    nombre = models.TextField(max_length=50)
    sql = models.TextField(max_length=1000)

    def __unicode__(self):
        return self.nombre

#---------------------------------------------------------------------------
#el balance de cada deudor.
class Balance(models.Model):
    #ficha del deudor al cual pertenece este balance
    ficha = models.ForeignKey(Ficha)
    
    #fecha del balance
    fecha = models.DateTimeField(null=False, default = datetime.now())

    #sumatoria de gastos judiciales
    costas = models.IntegerField(null=False, default=0 )

    #honorarios, calculados al momento de pagar la deuda
    honorario = models.IntegerField(null=False, default=0)
    
    #intereses, calculados en funcion del interes diario y del capital adeudado
    interes = models.IntegerField(null=False, default=0)

    #deuda inicial con falabella
    capital = models.IntegerField(null=False, default=0)


    a_capital = 0
    a_costas = 0
    a_interes = 0
    a_honorario = 0

    # entrega el saldo pendiente
    def saldo(self):
        return self.capital + self.costas + self.interes + self.honorario

    #retorna True si la deuda ha sido saldada.
    def pagada(self):
        if self.saldo(self) > 0:
            return True
        else:
            return False


    #calculo del interes en funcion de los dias transcurridos
    def calcula_interes(self, fecha_convenio):
        ficha = Ficha.objects.get(id = ficha)
        fecha_asignacion = ficha.fecha_creacion
        dias_transcurridos=abs(fecha_convenio - fecha_asignacion).days

        interes_diario=3.99/30
        interes = int(interes_diario *
                      dias_transcurridos *
                      self.capital / 100 )    

    # Calcula el honorario en funcion de si el caso paso a demanda o no.
    # En caso de que haya pasado a demanda el interes es mas alto.
    def calcula_honorario(self, hay_demanda):
        if hay_demanda:
            porc_honorario = 0.2
        else:
            porc_honorario = 0.15
        self.honorario = (self.capital + self.costas + self.interes)*porc_honorario
        
    def __unicode__(self):
        return u'capital:%d, costas:%d, interes:%d, honorario:%d SALDO_TOTAL:%d'%(self.capital, self.costas, self.interes, self.honorario, self.saldo())

    #accion de meterle plata al balance
    def abonar(self, abono, paso_a_tribunal):
        if abono <= 0:
            return -1
        elif abono > self.saldo():
            #el abono no puede ser mayor a la deuda total
            return -2
        else:
            #almacenamiento de valores inicial para hacer luego la diferencia de distribucion a cada item
            self.a_capital = self.capital
            self.a_costas = self.costas
            self.a_interes = self.interes
            self.a_honorario = self.honorario

            if paso_a_tribunal:
                abono_a_honorario = abono * 0.2
            else:
                abono_a_honorario = abono * 0.15
            
            if self.honorario > 0:
                self.honorario = self.honorario - abono_a_honorario
                abono_real = abono - abono_a_honorario
                if self.honorario < 0:
                    abono_real -= self.honorario
                    self.honorario = 0
            else:
                abono_real = abono

            if self.capital > 0:
                self.capital = self.capital - abono_real
                if self.capital < 0:
                    self.costas += self.capital #le restamos el resto de capital a las costas
                    self.capital = 0
                    if self.costas < 0:
                        self.interes += self.costas
                        self.costas = 0
            elif self.costas > 0:
                self.costas = self.costas - abono_real
                if self.costas < 0:
                    self.interes += self.costas
                    self.costas = 0
            elif interes > 0:
                self.interes = self.interes - abono_real

            #resto el valor final al final para saber la diferencia
            self.a_capital -= self.capital
            self.a_costas -= self.costas
            self.a_interes -= self.interes
            self.a_honorario -= self.honorario

            return True

