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

    def calcMAIndicators(self  , allTechnicalsList):

        keys = [ "ema10bullish", "ema20bullish" , "ema50bullish" , "sma10bullish", "sma20bullish" , "sma50bullish" ,
                 "dema10bullish", "dema20bullish" , "dema50bullish" ,  "wma10bullish", "wma20bullish" , "wma50bullish" ]

        maIndicatorList = []

        for technicals in allTechnicalsList:
            bullishCnt = 0
            bearishCnt = 0
            for key in keys:

                if technicals[key] == 1:
                    bullishCnt = bullishCnt + 1
                else:
                    bearishCnt = bearishCnt + 1

            maIndicatorList.append( {"coinpair" : technicals["coinpair"] , "bullishcnt" : bullishCnt , "bearishcnt" : bearishCnt})

            logger.info(technicals["coinpair"] + " Bullish " + str(bullishCnt) + " Bearish " + str(bearishCnt))

        return maIndicatorList




    def post(self , request):

        print("Printing inside Front page view")
        logger.info('Inside post Front page view')

        tradingStartTimeDict = Tradingtime.objects.order_by('-starttime').values('starttime').first()

        tradingStartTime = tradingStartTimeDict["starttime"]

        allTechnicals =  Technicals.objects.filter(Q(starttime = tradingStartTime)).values("pricechangepct" , "coinpair" , "unusualvolume" , "rsi",
                                                                                           "ema10bullish", "ema20bullish" , "ema50bullish" ,
                                                                                           "sma10bullish", "sma20bullish" , "sma50bullish" ,
                                                                                           "dema10bullish", "dema20bullish" , "dema50bullish" ,
                                                                                           "wma10bullish", "wma20bullish" , "wma50bullish" ,
                                                                                           "macdindicator")


        topgainers = sorted(allTechnicals , key= lambda k:k["pricechangepct"] , reverse=True).copy()
        toplosers = sorted(allTechnicals,key= lambda k:k["pricechangepct"]  ).copy()
        unusualVolume = sorted(allTechnicals, key= lambda k:k["unusualvolume"], reverse=True).copy()

        bullishMACDList =  [x for x in allTechnicals if x['macdindicator'] == 'Bullish']
        bearishMACDList = [x for x in allTechnicals if x['macdindicator'] == 'Bearish']

        macdList = []
        macdList.extend(bullishMACDList[:5])
        macdList.extend(bearishMACDList[:5])

        overboughtList = []
        oversoldList = []

        for technicals in allTechnicals:

            if technicals["rsi"] > 70:
                overboughtList.append(technicals)

            if technicals["rsi"] < 30:
                oversoldList.append(technicals)

        sortedOverBoughtList = sorted(overboughtList , key=lambda k:k["rsi"] , reverse=True).copy()
        sortedOverSoldList = sorted(oversoldList , key=lambda k:k["rsi"]).copy()

        maIndicatorList = self.calcMAIndicators(allTechnicals)
        sortedBullishMAList = sorted(maIndicatorList , key=lambda k:k["bullishcnt"] ,reverse=True).copy()
        sortedBearishMAList = sorted(maIndicatorList , key=lambda k:k["bearishcnt"] ,reverse=True).copy()

        bearishMAHeaders = [
            {"key": "coinpair", "name": "Coin Pair"},
            {"key": "bearishcnt", "name": "Bearish Indicators"}
        ]

        bullishMAHeaders = [
            {"key": "coinpair", "name": "Coin Pair"},
            {"key": "bullishcnt", "name": "Bullish Indicators"}
        ]

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

        macdHeaders = [
            {"key": "coinpair", "name": "Coin Pair"},
            {"key": "macdindicator", "name": "Bullish/Bearish"}
        ]





        response = {"frontpage": tradingStartTime ,
                    "bearishma" : Utils.filterKeys( sortedBearishMAList[:10] , ["coinpair" , "bearishcnt"]),
                    "bearishmaheaders" : bearishMAHeaders,
                    "bullishma": Utils.filterKeys(sortedBullishMAList[:10], ["coinpair", "bullishcnt"]),
                    "bullishmaheaders": bullishMAHeaders,
                    "macd" : Utils.filterKeys( macdList , ["coinpair" , "macdindicator"]),
                    "macdheaders": macdHeaders,
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
