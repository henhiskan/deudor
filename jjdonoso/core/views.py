from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.template import Context, loader

from django.core import serializers



login_needed = user_passes_test(lambda u: not u.is_anonymous(), login_url='/jjdonoso/login/')
  

from jjdonoso.core.models import *


def main(request):
    
    t = loader.get_template('index.html')
    c = Context({
            })
    return HttpResponse(t.render(c))



def ficha(request):
    
    t = loader.get_template('ficha.html')
    c = Context({
            })
    return HttpResponse(t.render(c))
    


def getdata(request):
    
    return HttpResponse('({"total":3,'\
                            '"results":[{"fecha":"2009/12/01","codigo":"23","descripcion":"empiea la deuda","pago":"contado","abono":"2121","gasto":"121","honorario":"1212"},{"fecha":"2009/11/21","codigo":"13","descripcion":"sigue la deuda","pago":"contado","abono":"55421","gasto":"54545","honorario":"323223"},{"fecha":"2009/11/11","codigo":"66","descripcion":"termina la deuda","pago":"contado","abono":"2121","gasto":"121","honorario":"1212"}]})',  mimetype="text/plain", content_type="application/json")


def getficha(request):

    json_serializer = serializer.get_serializer("json")()
    json_serializer.serialize(Ficha.objects.all(), ensure_ascii=False, stream=response)
    

    return HttpResponse(json_serializer, mimetupe="text/plain", content_type="application/json")
    
