from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout, logout_then_login

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    (r'^admin/', include(admin.site.urls)),
    (r'^$','core.views.main'),
    (r'^login/', login,{'template_name':'login.html'}),
    (r'^logout/$', logout_then_login,{'login_url':'/deudor/login/?next=/deudor/ficha'}) ,
    (r'^ficha','core.views.ficha'),
    (r'^getevento','core.views.getEvento'),
    (r'^getficha','core.views.getFicha'),
    (r'^getcodigo','core.views.getCodigo'),
    (r'^getformapago','core.views.getFormaPago'),
    (r'^getprocuradores','core.views.getProcuradores'),
    (r'^getreceptor','core.views.getReceptor'),
    (r'^getusuarios','core.views.getUsuarios'),
    (r'^gettribunales','core.views.getTribunales'),
    (r'^puteventoedit','core.views.putEventoEdit'),
    (r'^putevento','core.views.putEvento'),
    (r'^putdeudor','core.views.putDeudor'),
    (r'^putreporte','core.views.putReporte'),
    (r'^putficha','core.views.putFicha'),
    (r'^updatedeudor','core.views.updateDeudor'),
    (r'^getreporte','core.views.getReporte'),
    (r'^deleteevento','core.views.deleteEvento'),
    (r'^deleteficha','core.views.deleteFicha'),
    (r'^deudorjs','core.views.getDeudorJs'),
    (r'^cargarDatos','core.views.cargarDatos'),
                       
)
