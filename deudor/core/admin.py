from django.contrib import admin

from core.models import *

#class Generic(admin.ModelAdmin):
#    pass



admin.site.register(Usuario)#, Generic)
#admin.site.register(Persona)#, Generic)
admin.site.register(Codigo)#, Generic)
admin.site.register(Tribunal)#, Generic)
admin.site.register(FormaPago)
admin.site.register(Reporte)
admin.site.register(Receptor)
admin.site.register(SistemaOrigen)

class BalanceInline(admin.TabularInline):
    model = Balance
    extra = 1
    fields = ['fecha','capital','interes','costas','honorario']

class FichaAdmin(admin.ModelAdmin):
    list_display = ['persona','deuda_inicial']
    fields = ['persona','deuda_inicial']
    inlines = [BalanceInline]

admin.site.register(Ficha, FichaAdmin)
