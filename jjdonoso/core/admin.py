from django.contrib import admin

from jjdonoso.core.models import *

#class Generic(admin.ModelAdmin):
#    pass

admin.site.register(Usuario)#, Generic)
admin.site.register(Persona)#, Generic)
admin.site.register(Codigo)#, Generic)
admin.site.register(Tribunal)#, Generic)
admin.site.register(Ficha)#, Generic)
admin.site.register(Evento)#, Generic)

