from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Hourlydata
from .models import Technicals , Tradingtime
from django.db.models import Q
from datetime import timedelta
import logging
logger = logging.getLogger("app")
# Create your views here.


@csrf_protect
def index(request):
    # return HttpResponse('Hello from Python!')
    c = {}


    return render(request, 'index.html' ,c)

class Utils:

    @staticmethod
    def filterKeys(dictList , requiredKeys):

        finalList = []

        if len(dictList) > 0:
            for inputDict in dictList:
                entryDict = {}
                for requiredKey in requiredKeys:
                    valueTypeDict = {}
                    valueTypeDict["value"] = inputDict[requiredKey]

                    if type(inputDict[requiredKey]) is str:
                        valueTypeDict["type"] = "string"
                    elif type(inputDict[requiredKey]) is float:
                        valueTypeDict["type"] = "float"
                    elif type(inputDict[requiredKey]) is int:
                        valueTypeDict["type"] = "int"

                    entryDict[requiredKey] = valueTypeDict
                finalList.append(entryDict)

            logger.info(finalList)


        return finalList

class FrontPageView(APIView):



    def post(self , request):

        tradingStartTimeDict = Tradingtime.objects.order_by('-starttime').values('starttime').first()

        tradingStartTime = tradingStartTimeDict["starttime"]

        allTechnicals =  Technicals.objects.filter(Q(starttime = tradingStartTime)).values("pricechangepct" , "coinpair" , "unusualvolume" , "rsi")

        topgainers = sorted(allTechnicals , key= lambda k:k["pricechangepct"] , reverse=True).copy()
        toplosers = sorted(allTechnicals,key= lambda k:k["pricechangepct"]  ).copy()
        unusualVolume = sorted(allTechnicals, key= lambda k:k["unusualvolume"], reverse=True).copy()

        overboughtList = []
        oversoldList = []

        for technicals in allTechnicals:

            if technicals["rsi"] > 70:
                overboughtList.append(technicals)

            if technicals["rsi"] < 30:
                oversoldList.append(technicals)

        sortedOverBoughtList = sorted(overboughtList , key=lambda k:k["rsi"] , reverse=True).copy()
        sortedOverSoldList = sorted(oversoldList , key=lambda k:k["rsi"]).copy()

        topgainersHeaders = [
            { "key" : "coinpair" , "name" : "Coin Pair" } ,
            {"key": "pricechangepct", "name": "Price Change (%)"}
        ]

        toplosersHeaders = [
            {"key": "coinpair", "name": "Coin Pair"},
            {"key": "pricechangepct", "name": "Price Change (%)"}
        ]

        unusualVolumeHeaders = [
            {"key": "coinpair", "name": "Coin Pair"},
            {"key": "unusualvolume", "name": "Unusual Volume"}
        ]

        overboughtHeaders  = [
            {"key": "coinpair", "name": "Coin Pair"},
            {"key": "rsi", "name": "RSI"}
        ]

        oversoldHeaders = [
            {"key": "coinpair", "name": "Coin Pair"},
            {"key": "rsi", "name": "RSI"}
        ]



        response = {"frontpage": tradingStartTime ,
                    "topgainers" : Utils.filterKeys(topgainers[:10] , [ "coinpair" , "pricechangepct" ]) ,
                    "topgainersheaders" : topgainersHeaders,
                    "toplosers" : Utils.filterKeys(toplosers[:10] , ["pricechangepct" , "coinpair"]) ,
                    "toplosersheaders" : toplosersHeaders,
                    "unusualvolume": Utils.filterKeys(unusualVolume[:10] , ["unusualvolume" , "coinpair"]) ,
                    "unusualvolumeheaders" : unusualVolumeHeaders,
                    "overbought" : Utils.filterKeys(sortedOverBoughtList[:10] , ["rsi" , "coinpair"]) ,
                    "overboughtheaders" : overboughtHeaders,
                    "oversold" : Utils.filterKeys(sortedOverSoldList[:10] , ["rsi" , "coinpair"]) ,
                    "oversoldheaders" : oversoldHeaders
                    }

        return Response(response)


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
