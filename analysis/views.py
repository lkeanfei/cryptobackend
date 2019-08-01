from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Hourlydata
from django.db.models import Q
import logging
logger = logging.getLogger("app")
# Create your views here.


@csrf_protect
def index(request):
    # return HttpResponse('Hello from Python!')
    c = {}


    return render(request, 'index.html' ,c)


class HourlyDataView(APIView):

    def post(self ,request):

        rows = Hourlydata.objects.filter( Q(open__gte = 9800)).values('open' , 'high' , 'low' , 'close')

        logger.info("Num rows " + str(len(rows)))

        # for row in rows:
        #     logger.info(row)

        res = {}
        return Response(rows)

class HelloApiView(APIView):



    def get(self , request , format=None):
        an_apiview = [
            'Hello Api 123',
            '456',
            '789',
        ]



        return Response( {'message' : 'HelloApiView '} )

    def post(self , request , format=None):
        an_apiview = [
            'Post Api 123',
            '456',
            '789',
        ]

        return Response({'message': 'HelloApiView '})
