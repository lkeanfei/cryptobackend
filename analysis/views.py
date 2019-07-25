from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.


@csrf_protect
def index(request):
    # return HttpResponse('Hello from Python!')
    c = {}


    return render(request, 'index.html' ,c)


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
