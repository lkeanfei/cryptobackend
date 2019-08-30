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
    def getDictKeys(dictList):

        keyList= []
        for dict in dictList:
            keyList.append(dict["key"])

        return keyList



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

            maIndicatorList.append( {"exchange" : technicals["exchange"] , "coinpair" : technicals["coinpair"] , "bullishcnt" : bullishCnt , "bearishcnt" : bearishCnt})

            # logger.info(technicals["coinpair"] + " Bullish " + str(bullishCnt) + " Bearish " + str(bearishCnt))

        return maIndicatorList




    def post(self , request):

        print("Printing inside Front page view")
        logger.info('Inside post Front page view')
        logger.info(request.method)
        logger.info(request.POST)
        logger.info(request.data.keys())


        tradingStartTimeDict = Tradingtime.objects.order_by('-starttime').values('starttime').first()

        logger.info('Trading start Time')
        logger.info(tradingStartTimeDict)

        tradingStartTime = tradingStartTimeDict["starttime"]

        logger.info('Finished getting technicals')

        allTechnicals =  Technicals.objects.filter(Q(starttime = tradingStartTime)).values("pricechangepct" , "coinpair" , "unusualvolume" , "rsi",
                                                                                           "ema10bullish", "ema20bullish" , "ema50bullish" ,
                                                                                           "sma10bullish", "sma20bullish" , "sma50bullish" ,
                                                                                           "dema10bullish", "dema20bullish" , "dema50bullish" ,
                                                                                           "wma10bullish", "wma20bullish" , "wma50bullish" ,
                                                                                           "macdindicator" , "exchange")

        logger.info('Finished getting technicals')


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
            {"key": "exchange", "name": "Exchange"},
            {"key": "coinpair", "name": "Coin Pair"},
            {"key": "bearishcnt", "name": "Bearish Indicators"}
        ]

        bullishMAHeaders = [
            {"key": "exchange", "name": "Exchange"},
            {"key": "coinpair", "name": "Coin Pair"},
            {"key": "bullishcnt", "name": "Bullish Indicators"}
        ]

        topgainersHeaders = [
            { "key" : "exchange" , "name" : "Exchange" },
            { "key" : "coinpair" , "name" : "Coin Pair" } ,
            {"key": "pricechangepct", "name": "Price Change (%)"}
        ]

        toplosersHeaders = [
            {"key": "exchange", "name": "Exchange"},
            {"key": "coinpair", "name": "Coin Pair"},
            {"key": "pricechangepct", "name": "Price Change (%)"}
        ]

        unusualVolumeHeaders = [
            {"key": "exchange", "name": "Exchange"},
            {"key": "coinpair", "name": "Coin Pair"},
            {"key": "unusualvolume", "name": "Unusual Volume"}
        ]

        overboughtHeaders  = [
            {"key": "exchange", "name": "Exchange"},
            {"key": "coinpair", "name": "Coin Pair"},
            {"key": "rsi", "name": "RSI"}
        ]

        oversoldHeaders = [
            {"key": "exchange", "name": "Exchange"},
            {"key": "coinpair", "name": "Coin Pair"},
            {"key": "rsi", "name": "RSI"}
        ]

        macdHeaders = [
            {"key": "exchange", "name": "Exchange"},
            {"key": "coinpair", "name": "Coin Pair"},
            {"key": "macdindicator", "name": "Bullish/Bearish"}
        ]

        bmaList =  Utils.getDictKeys(bearishMAHeaders)
        print(bmaList)

        response = {"frontpage": tradingStartTime ,
                    "bearishma" : Utils.filterKeys( sortedBearishMAList[:10] , bmaList),
                    "bearishmaheaders" : bearishMAHeaders,
                    "bullishma": Utils.filterKeys(sortedBullishMAList[:10], Utils.getDictKeys(bullishMAHeaders)),
                    "bullishmaheaders": bullishMAHeaders,
                    "macd" : Utils.filterKeys( macdList , Utils.getDictKeys(macdHeaders)),
                    "macdheaders": macdHeaders,
                    "topgainers" : Utils.filterKeys(topgainers[:10] , Utils.getDictKeys(topgainersHeaders)) ,
                    "topgainersheaders" : topgainersHeaders,
                    "toplosers" : Utils.filterKeys(toplosers[:10] , Utils.getDictKeys(toplosersHeaders)) ,
                    "toplosersheaders" : toplosersHeaders,
                    "unusualvolume": Utils.filterKeys(unusualVolume[:10] ,Utils.getDictKeys(unusualVolumeHeaders)) ,
                    "unusualvolumeheaders" : unusualVolumeHeaders,
                    "overbought" : Utils.filterKeys(sortedOverBoughtList[:10] , Utils.getDictKeys(overboughtHeaders)) ,
                    "overboughtheaders" : overboughtHeaders,
                    "oversold" : Utils.filterKeys(sortedOverSoldList[:10] , Utils.getDictKeys(oversoldHeaders)) ,
                    "oversoldheaders" : oversoldHeaders
                    }

        return Response(response)



class TechnicalsSummaryView(APIView):

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

            maIndicatorList.append( {"exchange" : technicals["exchange"] , "coinpair" : technicals["coinpair"] , "bullishcnt" : bullishCnt , "bearishcnt" : bearishCnt})

            # logger.info(technicals["coinpair"] + " Bullish " + str(bullishCnt) + " Bearish " + str(bearishCnt))

        return maIndicatorList




    def post(self , request):

        exchange = ""
        exchangeList = ["Bitfinex", "BitTrex" , "Binance" , "OKEx" , "DigiFinex" , "HitBTC" , "Kucoin" , "Huobi Global"]
        response = {}
        if "exchange" in request.data.keys():
            exchange = request.data["exchange"]

            if exchange in exchangeList:

                print("Technicals Summary " + exchange )

                tradingStartTimeDict = Tradingtime.objects.order_by('-starttime').values('starttime').first()

                logger.info('Trading start Time')
                logger.info(tradingStartTimeDict)

                tradingStartTime = tradingStartTimeDict["starttime"]

                logger.info('Finished getting technicals')
                technicalskwargs = {}
                technicalskwargs["starttime"] = tradingStartTime
                technicalskwargs["exchange"] = exchange

                allTechnicals =  Technicals.objects.filter(**technicalskwargs).values("pricechangepct" , "coinpair" , "unusualvolume" , "rsi",
                                                                                                   "ema10bullish", "ema20bullish" , "ema50bullish" ,
                                                                                                   "sma10bullish", "sma20bullish" , "sma50bullish" ,
                                                                                                   "dema10bullish", "dema20bullish" , "dema50bullish" ,
                                                                                                   "wma10bullish", "wma20bullish" , "wma50bullish" ,
                                                                                                   "macdindicator" , "exchange")

                logger.info('Finished getting technicals')


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
                    {"key": "exchange", "name": "Exchange"},
                    {"key": "coinpair", "name": "Coin Pair"},
                    {"key": "bearishcnt", "name": "Bearish Indicators"}
                ]

                bullishMAHeaders = [
                    {"key": "exchange", "name": "Exchange"},
                    {"key": "coinpair", "name": "Coin Pair"},
                    {"key": "bullishcnt", "name": "Bullish Indicators"}
                ]

                topgainersHeaders = [
                    { "key" : "exchange" , "name" : "Exchange" },
                    { "key" : "coinpair" , "name" : "Coin Pair" } ,
                    {"key": "pricechangepct", "name": "Price Change (%)"}
                ]

                toplosersHeaders = [
                    {"key": "exchange", "name": "Exchange"},
                    {"key": "coinpair", "name": "Coin Pair"},
                    {"key": "pricechangepct", "name": "Price Change (%)"}
                ]

                unusualVolumeHeaders = [
                    {"key": "exchange", "name": "Exchange"},
                    {"key": "coinpair", "name": "Coin Pair"},
                    {"key": "unusualvolume", "name": "Unusual Volume"}
                ]

                overboughtHeaders  = [
                    {"key": "exchange", "name": "Exchange"},
                    {"key": "coinpair", "name": "Coin Pair"},
                    {"key": "rsi", "name": "RSI"}
                ]

                oversoldHeaders = [
                    {"key": "exchange", "name": "Exchange"},
                    {"key": "coinpair", "name": "Coin Pair"},
                    {"key": "rsi", "name": "RSI"}
                ]

                macdHeaders = [
                    {"key": "exchange", "name": "Exchange"},
                    {"key": "coinpair", "name": "Coin Pair"},
                    {"key": "macdindicator", "name": "Bullish/Bearish"}
                ]

                bmaList =  Utils.getDictKeys(bearishMAHeaders)
                print(bmaList)

                response = {"frontpage": tradingStartTime ,
                            "bearishma" : Utils.filterKeys( sortedBearishMAList[:10] , bmaList),
                            "bearishmaheaders" : bearishMAHeaders,
                            "bullishma": Utils.filterKeys(sortedBullishMAList[:10], Utils.getDictKeys(bullishMAHeaders)),
                            "bullishmaheaders": bullishMAHeaders,
                            "macd" : Utils.filterKeys( macdList , Utils.getDictKeys(macdHeaders)),
                            "macdheaders": macdHeaders,
                            "topgainers" : Utils.filterKeys(topgainers[:10] , Utils.getDictKeys(topgainersHeaders)) ,
                            "topgainersheaders" : topgainersHeaders,
                            "toplosers" : Utils.filterKeys(toplosers[:10] , Utils.getDictKeys(toplosersHeaders)) ,
                            "toplosersheaders" : toplosersHeaders,
                            "unusualvolume": Utils.filterKeys(unusualVolume[:10] ,Utils.getDictKeys(unusualVolumeHeaders)) ,
                            "unusualvolumeheaders" : unusualVolumeHeaders,
                            "overbought" : Utils.filterKeys(sortedOverBoughtList[:10] , Utils.getDictKeys(overboughtHeaders)) ,
                            "overboughtheaders" : overboughtHeaders,
                            "oversold" : Utils.filterKeys(sortedOverSoldList[:10] , Utils.getDictKeys(oversoldHeaders)) ,
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
