from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^jjdonoso/', include('jjdonoso.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^$','jjdonoso.core.views.main'),
    (r'^ficha','jjdonoso.core.views.ficha'),
    (r'^getevento','jjdonoso.core.views.getEvento'),
    (r'^getficha','jjdonoso.core.views.getFicha'),
    (r'^getcodigo','jjdonoso.core.views.getCodigo'),
    (r'^getformapago','jjdonoso.core.views.getFormaPago'),
    (r'^getprocuradores','jjdonoso.core.views.getProcuradores'),
    (r'^gettribunales','jjdonoso.core.views.getTribunales'),
    (r'^putevento','jjdonoso.core.views.putEvento'),
    (r'^putdeudor','jjdonoso.core.views.putDeudor'),
    (r'^putreporte','jjdonoso.core.views.putReporte'),
    (r'^getreporte','jjdonoso.core.views.getReporte'),
                       
)
