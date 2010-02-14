from django.contrib import admin

from core.models import *

#class Generic(admin.ModelAdmin):
#    pass

admin.site.register(Usuario)#, Generic)
admin.site.register(Persona)#, Generic)
admin.site.register(Codigo)#, Generic)
admin.site.register(Tribunal)#, Generic)
admin.site.register(Ficha)#, Generic)
admin.site.register(FormaPago)
admin.site.register(Reporte)
admin.site.register(Evento)#, Generic)
admin.site.register(Receptor)

