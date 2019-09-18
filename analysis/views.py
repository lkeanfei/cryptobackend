from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Hourlydata
from .models import Technicals , Tradingtime , Hourlydatatechnicalsview , Technicalsavailablecoinpairs, Technicalsavailablemarkets , Geckofundamentals ,Geckopricevolume , Geckocoinpair
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
    def getTradingStartTime():

        tradingStartTimeDict = Tradingtime.objects.order_by('-starttime').values('starttime').first()

        return tradingStartTimeDict["starttime"]

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


class ArchiveCoinPairSummaryView(APIView):

    def post(self,request):

        response = {}

        if 'coinpair' in request.data.keys():

            # Get latest trading time
            startTime = Tradingtime.objects.order_by('-starttime').values('starttime')[0]



            # Technicals
            technicalsKwargs = {}
            technicalsKwargs['starttime'] = startTime['starttime']
            technicalsKwargs['coinpair'] = request.data['coinpair']

            bullishKeys = [ 'dema10bullish' , 'dema20bullish' , 'dema50bullish' , 'ema10bullish' , 'ema20bullish' , 'ema50bullish', 'sma10bullish' , 'sma20bullish' , 'sma50bullish' ,
                            'wma10bullish' , 'wma20bullish' , 'wma50bullish']

            technicalRows = Technicals.objects.filter(**technicalsKwargs).values('starttime' , 'exchange' , 'coinpair' , 'rsi', 'dema10bullish' , 'dema20bullish' , 'dema50bullish' ,
                                                                                 'ema10bullish' , 'ema20bullish' , 'ema50bullish', 'sma10bullish' , 'sma20bullish' , 'sma50bullish' ,
                                                                                 'wma10bullish' , 'wma20bullish' , 'wma50bullish')

            technicalSummaryList = []

            for technical in technicalRows:
                bullishCnt = 0
                bearishCnt = 0
                summaryDict= {}
                summaryDict["exchange"] = technical["exchange"]
                for key in bullishKeys:
                    if technical[key] == 1:
                        bullishCnt = bullishCnt + 1
                    else:
                        bearishCnt = bearishCnt + 1
                summaryDict["bullishcnt"] = bullishCnt
                summaryDict["bearishcnt"] = bearishCnt
                summaryDict["rsi"] = technical["rsi"]
                technicalSummaryList.append(summaryDict)

            coinpairheaders = [ {
                "key" : "exchange",
                "name" : "Exchange"
            } ,
                {
                    "key" : "bullishcnt",
                    "name" : "Bullish MAs"
                }
                ,
                {
                    "key": "bearishcnt",
                    "name": "Bearsh MAs"
                }
            ]


            coinpairDataList = []
            for technicalSummary in technicalSummaryList:
                coinpairDataDict ={}
                for key in technicalSummary.keys():
                    value = technicalSummary[key]
                    type = "string"
                    if isinstance(value ,str):
                        type = "string"
                    elif isinstance(value ,int):
                        type = "int"
                    coinpairDataDict[key] = { "value" : value , "type" : type}
                coinpairDataList.append(coinpairDataDict)

            response["coinpairdata"] = coinpairDataList
            response["coinpairheaders"] = coinpairheaders





        return Response(response)


class AvailableCoinPairsView(APIView):

    def get(self, request):

        response = {}

        coinpairs = Technicalsavailablecoinpairs.objects.all().values('coinpair')

        coinpairList = []
        for coinpair in coinpairs:
            coinpairList.append(coinpair["coinpair"])

        response["results"] = coinpairList

        return Response(response)




class AvailableMarketsView(APIView):

    def get(self ,request):

        response = {}

        markets = Technicalsavailablemarkets.objects.all().values('exchange')
        response["results"] = markets

        return Response(response)

class CoinView(APIView):

    def post(self , request):

        # Get the latest trading time

        response = {}

        if "coin" in request.data.keys():

            symbol = request.data["coin"]

            tradingStartTime = Utils.getTradingStartTime()

            geckoPriceVolumeKwargs = {}
            geckoPriceVolumeKwargs["starttime"] = tradingStartTime
            geckoPriceVolumeKwargs["coinid__symbol"] = symbol

            fundamentals = Geckofundamentals.objects.filter(**geckoPriceVolumeKwargs).values('blocktime' , 'developer' , 'community' , 'liquidity' , 'publicinterest' , 'description')
            priceVolumes = Geckopricevolume.objects.filter(**geckoPriceVolumeKwargs).values('total_volume' , 'price_change_24h' , 'current_price' ,
                                                                                            'high_24h' , 'low_24h' , 'price_change_percentage_24h' , 'price_change_percentage_7d' ,
                                                                                            'market_cap' , 'market_cap_change_percentage_24h')

            geckoCoinPairKwargs = {}
            geckoCoinPairKwargs["coin__iexact"] = symbol

            geckoCoinPairs = Geckocoinpair.objects.filter(**geckoCoinPairKwargs).values("coinpair")
            allCoinPairRows = []

            for row in geckoCoinPairs:
                coinPair = row["coinpair"]
                coinPairDict = {}

                logger.info('Finished getting technicals' + coinPair)
                technicalsKwargs = {}
                technicalsKwargs["coinpair"] = coinPair
                technicalsKwargs["starttime"] = tradingStartTime

                summaryRows = Hourlydatatechnicalsview.objects.filter(**technicalsKwargs).values("coinpair" , "market" , "close" , "volume" , "pricechangepct", "rsi")

                allCoinPairRows.extend(summaryRows)

            coinPairKeys = ["coinpair", "market", "close", "volume", "pricechangepct" , "rsi"]
            coinPairHeaders = [{  "key": "coinpair",  "name": "Coin Pair" } ,
                               { "key" : "market" , "name" : "Market"} ,
                               { "key" : "close" , "name" : "Last" },
                               {"key" : "volume" , "name" : "Volume (1h)" },
                               { "key" : "pricechangepct" , "name" : "Price Change (1h) %"} ,
                               {"key" : "rsi" , "name" : "RSI"}
                                 ]

            response["fundamentals"] = fundamentals
            response["pricevolume"] = priceVolumes

            coinpairList = []

            for resDict in allCoinPairRows:
                coinPairCell = {}
                for key in coinPairKeys:
                    valType = "string"
                    if key == "coinpair":
                        valType = "link"
                        coinPairCell[key] = {"value": resDict[key], "type": valType , "link" : "/coinpair/"+ resDict[key] }

                    elif type(resDict[key]) is str:
                        valType = "string"
                        coinPairCell[key] = {"value": resDict[key], "type": valType}
                    elif type(resDict[key]) is float:
                        valType = "float"
                        coinPairCell[key] = {"value": resDict[key], "type": valType}
                    elif type(resDict[key]) is int:
                        valType = "int"
                        coinPairCell[key] = {"value": resDict[key], "type": valType}

                    # fundColumn[key] = { "value" : resDict[key] , "type" : valType}

                coinpairList.append(coinPairCell)

            response["data"] = coinpairList
            response["headers"] = coinPairHeaders

        return Response(response)



class CoinPairView(APIView):

    def post(self , request):
        response = {}

        if "coinpair" in request.data.keys():
            print("")
            coinpair = request.data["coinpair"]

            tradingStartTime = Utils.getTradingStartTime()

            filterKwargs = {}
            filterKwargs["coinpair__iexact"] = coinpair
            filterKwargs["starttime"] = tradingStartTime

            summaryRows = Hourlydatatechnicalsview.objects.filter(**filterKwargs).values("coinpair", "market",
                                                                                             "close", "volume", "upperband","midband","lowerband",
                                                                                         "dema10","ema10","sar","sma10","wma10","ad","obv","atr","adx","aroonosc","dx","macd","macdsignal","macdhist","mfi",
                                                                                         "dema20","ema20","sma20","wma20", "dema50","ema50","sma50","wma50",
                                                                                         "rsi","pricechangepct","unusualvolume","macdindicator")

            movingAverageKeys = [ "indicator" , "value" ]
            movingAverageHeaders = [{"key" : "indicator" , "name" : "Indicator"} ,
                                    {"key" : "value" , "name" : "Value"}]

            allMovingAverageList = []
            marketDict = {}
            markets =[]

            for summaryRow in summaryRows:

                market = summaryRow["market"]

                markets.append(market)
                ema10 = summaryRow["ema10"]
                marketMovAverageList = []

                marketMovingAverage = {}
                marketMovingAverage["indicator"] = { "value" : "Exponential Moving Average(10)" , "type" : "string"}
                marketMovingAverage["value"] = {"value" : ema10 , "type" : "float"}
                marketMovAverageList.append(marketMovingAverage)

                dema10 = summaryRow["dema10"]
                dema10dict = {}
                dema10dict["indicator"] =  { "value" : "Double Exponential Moving Average(10)" , "type" : "string"}
                dema10dict["value"] = {"value" : dema10 , "type" : "float"}
                marketMovAverageList.append(dema10dict)

                wma10 = summaryRow["wma10"]
                wma10dict = {}
                wma10dict["indicator"] = {"value": "Weighted Moving Average(10)", "type": "string"}
                wma10dict["value"] = {"value": wma10, "type": "float"}
                marketMovAverageList.append(wma10dict)

                sma10 = summaryRow["sma10"]
                sma10dict = {}
                sma10dict["indicator"] = {"value": "Simple Moving Average(10)", "type": "string"}
                sma10dict["value"] = {"value": sma10, "type": "float"}
                marketMovAverageList.append(sma10dict)

                ema20 = summaryRow["ema20"]
                ema20dict = {}
                ema20dict["indicator"] = {"value": "Exponential Moving Average(20)", "type": "string"}
                ema20dict["value"] = {"value": ema20, "type": "float"}
                marketMovAverageList.append(ema20dict)

                dema20 = summaryRow["dema20"]
                dema20dict = {}
                dema20dict["indicator"] = {"value": "Double Exponential Moving Average(20)", "type": "string"}
                dema20dict["value"] = {"value": dema20, "type": "float"}
                marketMovAverageList.append(dema20dict)

                wma20 = summaryRow["wma20"]
                wma20dict = {}
                wma20dict["indicator"] = {"value": "Weighted Moving Average(20)", "type": "string"}
                wma20dict["value"] = {"value": wma20, "type": "float"}
                marketMovAverageList.append(wma20dict)

                sma20 = summaryRow["sma20"]
                sma20dict = {}
                sma20dict["indicator"] = {"value": "Simple Moving Average(20)", "type": "string"}
                sma20dict["value"] = {"value": sma20, "type": "float"}
                marketMovAverageList.append(sma20dict)

                ema50 = summaryRow["ema50"]
                ema50dict = {}
                ema50dict["indicator"] = {"value": "Exponential Moving Average(50)", "type": "string"}
                ema50dict["value"] = {"value": ema50, "type": "float"}
                marketMovAverageList.append(ema50dict)

                dema50 = summaryRow["dema50"]
                dema50dict = {}
                dema50dict["indicator"] = {"value": "Double Exponential Moving Average(50)", "type": "string"}
                dema50dict["value"] = {"value": dema50, "type": "float"}
                marketMovAverageList.append(dema50dict)

                wma50 = summaryRow["wma50"]
                wma50dict = {}
                wma50dict["indicator"] = {"value": "Weighted Moving Average(50)", "type": "string"}
                wma50dict["value"] = {"value": wma50, "type": "float"}
                marketMovAverageList.append(wma50dict)

                sma50 = summaryRow["sma50"]
                sma50dict = {}
                sma50dict["indicator"] = {"value": "Simple Moving Average(50)", "type": "string"}
                sma50dict["value"] = {"value": sma50, "type": "float"}
                marketMovAverageList.append(sma50dict)

                marketDict[market] =  marketMovAverageList

            response["markets"] = markets
            response["results"] = summaryRows
            response["movingaverages"] = marketDict
            response["movingaveragesheaders"] = movingAverageHeaders



        return Response(response)







class FrontPageView(APIView):

    def post(self,request):

        # First get the tradingtime
        tradingStartTime = Utils.getTradingStartTime()

        frontPageKwargs = {}
        frontPageKwargs["starttime"] = tradingStartTime

        fundamentalsRows = Geckofundamentals.objects.filter(**frontPageKwargs).order_by("-liquidity").values("coinid__name" , "coinid__symbol" , "blocktime" , "developer" , "community" , "liquidity" , "publicinterest" , "description")

        response = {}

        print("Length is " + str(len(fundamentalsRows)))


        fundamentalsKeys = ["coinid__name" , "developer" , "community" , "liquidity" , "publicinterest"]

        fundamentalsHeaders = [{
            "key": "coinid__name",
            "name": "Coin"
        },
            {
                "key": "developer",
                "name": "Developer Score"
            }
            ,
            {
                "key": "community",
                "name": "Community Score"
            }
            ,
            {
                "key": "liquidity",
                "name": "Liquidity Score"
            }
            ,
            {
                "key": "publicinterest",
                "name": "Public interest score"
            }
        ]

        response["headers"] = fundamentalsHeaders
        fundList = []

        for resDict in fundamentalsRows:
            fundColumn = {}
            for key in fundamentalsKeys:
                valType = "string"
                if key == "coinid__name":
                    valType = "link"
                    fundColumn[key] = {"value": resDict[key], "type": valType , "link" : "/coin/" + resDict["coinid__symbol"]}
                elif type(resDict[key]) is str:
                    valType = "string"
                    fundColumn[key] = {"value": resDict[key], "type": valType}
                elif type(resDict[key]) is float:
                    valType = "float"
                    fundColumn[key] = {"value": resDict[key], "type": valType}
                elif type(resDict[key]) is int:
                    valType = "int"
                    fundColumn[key] = {"value": resDict[key], "type": valType}

                # fundColumn[key] = { "value" : resDict[key] , "type" : valType}

            fundList.append(fundColumn)

        response["data"] = fundList

        return Response(response)





class ArchiveFrontPageView(APIView):

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

            if exchange == "HuobiGlobal":
                exchange = "Huobi Global"

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
