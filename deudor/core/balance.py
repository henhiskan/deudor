from datetime import date

class Balance:
    capital = 0
    costas = 0
    interes = 0
    honorario = 0
    #montos finalmente abonados a cada cuenta
    a_capital = 0
    a_costas = 0
    a_interes = 0
    a_honorario = 0

    def __init__(self, capital, costas, interes):
        self.capital = capital
        self.costas = costas
        self.interes = interes 
        self.honorario = 0
        self.a_capital = 0
        self.a_costas = 0
        self.a_interes = 0
        self.a_honorario = 0

    def set_capital(self, capital):
        self.capital = capital

    def set_costas(self, costas):
        self.costas = costas

    def set_interes(self, interes):
        self.interes = interes

    def set_honorario(self, honorario):
        self.honorario = honorario

    #retorna True si la deuda ha sido saldada.
    def pagada(self):
        if self.saldo(self) > 0:
            return True
        else:
            return False

    # entrega el saldo pendiente
    def saldo(self):
        return self.capital + self.costas + self.interes + self.honorario

    #calculo del interes en funcion de los dias transcurridos
    def calcula_interes(fecha_convenio):
        dias_transcurridos=abs(fecha_convenio-self.fecha_asignacion).days
        #print '%d dias transcurridos'%dias_transcurridos
        self.interes = int(self.interes_diario *
                           dias_transcurridos *
                           self.capital / 100 )    

    # Calcula el honorario en funcion de si el caso paso a demanda o no.
    # En caso de que haya pasado a demanda el interes es mas alto.
    def calcula_honorario(self,hay_demanda):
        if hay_demanda:
            porc_honorario = 0.2
        else:
            porc_honorario = 0.15
        self.honorario = (self.capital + self.costas + self.interes)*porc_honorario
        
    def __str__(self):
        return 'capital:%d, costas:%d, interes:%d, honorario:%d SALDO_TOTAL:%d'%(self.capital, self.costas, self.interes, self.honorario, self.saldo())

    #accion de meterle plata al balance
    def abonar(self,abono, paso_a_tribunal):
        if abono <= 0:
            #print 'abono debe ser mayor a 0'
            return False
        elif abono > self.saldo():
            #print 'el abono no puede ser mayor a la deuda total'
            return False
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
                    abono_real-=self.honorario
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
                    self.interes+= self.costas
                    self.costas = 0
            elif self.interes > 0:
                self.interes = self.interes - abono_real

            #resto el valor final al final para saber la diferencia
            self.a_capital -= self.capital
            self.a_costas -= self.costas
            self.a_interes -= self.interes
            self.a_honorario -= self.honorario

            return True

#dato del sistema
interes_diario = 3.99/30 

#las siguientes son variables externas que deben ser obtenidas.
hay_demanda=True #si hay demanda la comision es mayor(20%). Sino es 15%
fecha_asig = date(2010,3,1) #fecha de asignacion de la causa

deuda_inicial = 200000
total_gastos_judiciales = 20000

if __name__ == '__main__':
    bal = Balance(100000,20000,21000)
    bal.calcula_honorario(True)

    TOTAL_ABONADO = 0
    while bal.saldo() > 0:
        print bal
        
        uin=raw_input("ingrese abono: ").strip()
        try:
            abono=int(uin)
        except:
            print 'debe ingresar un numero entero. Reintente.'
        
        if bal.abonar(abono, True):
            TOTAL_ABONADO+=abono
            print 'a capital:%d'%bal.a_capital
            print 'a costas:%d'%bal.a_costas
            print 'a interes:%d'%bal.a_interes
            print 'a honorario:%d'%bal.a_honorario
        
            
    print '------------------------------------'
    print 'deuda saldada. TOTAL ABONADO = %d'%TOTAL_ABONADO
    print bal

    
        

