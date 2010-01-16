from django.template import Library
from django.contrib.auth.models import User

from deudor.core.models import *



register = Library()
@register.filter('getTipoUsuario')
def getTipoUsuario(value):
    """ Entrega el tipo de usuario """


    if value.usuario_set.count() > 0:
        usuario = value.usuario_set.get()
        return usuario.get_perfil_display()
    else:
        return value
    
