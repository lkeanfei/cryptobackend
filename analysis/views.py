from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Hourlydata
from .models import Technicals , Tradingtime , Hourlydatatechnicalsview , Technicalsavailablecoinpairs, Technicalsavailablemarkets , Geckofundamentals ,Geckopricevolume , Geckocoinpair
from django.db.models import Q
from datetime import timedelta ,datetime

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
            geckoPriceVolumeKwargs["starttime__lte"] = tradingStartTime
            geckoPriceVolumeKwargs["coinid__symbol"] = symbol

            fundamentals = Geckofundamentals.objects.filter(**geckoPriceVolumeKwargs).values('blocktime' , 'developer' , 'community' , 'liquidity' , 'publicinterest' , 'description')
            priceVolumes = Geckopricevolume.objects.filter(**geckoPriceVolumeKwargs).values('starttime' , 'total_volume' , 'price_change_24h' , 'current_price' ,
                                                                                            'high_24h' , 'low_24h' , 'price_change_percentage_24h' , 'price_change_percentage_7d' ,
                                                                                            'market_cap' , 'market_cap_change_percentage_24h').order_by("starttime")

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

            dateseries = []
            closeseries = []

            for priceVol in priceVolumes:
                dateseries.append(priceVol["starttime"])
                closeseries.append(priceVol["current_price"])

            response["fundamentals"] = fundamentals
            response["pricevolume"] = priceVolumes
            response["dateseries"] = dateseries
            response["closeseries"] = closeseries
            logger.info(tradingStartTime)
            logger.info(symbol + " Price volumes is " + str(len(priceVolumes)))

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

        startTime = datetime.now()

        if "coinpair" in request.data.keys():
            print("")
            coinpair = request.data["coinpair"]

            tradingStartTime = Utils.getTradingStartTime()

            rangeStartTime = tradingStartTime - timedelta(days=30)

            filterKwargs = {}
            filterKwargs["coinpair__iexact"] = coinpair
            filterKwargs["starttime__gte"] = rangeStartTime



            summaryRows = Hourlydatatechnicalsview.objects.filter(**filterKwargs).values( "starttime" ,"coinpair", "market", "open" , "high", "low" ,
                                                                                             "close", "volume", "upperband","midband","lowerband",
                                                                                         "dema10","ema10","sar","sma10","wma10","ad","obv","atr","adx","aroonosc","dx","macd","macdsignal","macdhist","mfi",
                                                                                         "dema20","ema20","sma20","wma20", "dema50","ema50","sma50","wma50",
                                                                                         "rsi","pricechangepct","unusualvolume","macdindicator")

            timeD = datetime.now() - startTime

            logger.info('Delta ' + str(timeD.total_seconds()))


            latestTradeRows = [d for d in summaryRows if d["starttime"] == tradingStartTime]

            trend_keys = ["sar" , "adx" ,"macd" , "aroonosc"]
            trend_headers = [{"key" : "indicator" , "name" : "Indicator"} ,
                                    {"key" : "value" , "name" : "Value"}]

            trend_dict = {}

            for summaryRow in latestTradeRows:
                market = summaryRow["market"]
                trend_list = []

                sar = summaryRow["sar"]
                sarDict = {}
                sarDict["indicator"] = { "value" : "Parabolic SAR" , "type" : "string"}
                sarDict["value"] = { "value" : sar , "type" : "float"}
                trend_list.append(sarDict)

                adx = summaryRow["adx"]
                adxDict = {}
                adxDict["indicator"] = { "value" : "ADX" , "type" : "string"}
                adxDict["value"] = { "value" : adx , "type" : "float"}
                trend_list.append(adxDict)

                aroon_osc = summaryRow["aroonosc"]
                aroonDict = {}
                aroonDict["indicator"] = { "value" : "Aroon Oscilator" , "type" : "string"}
                aroonDict["value"] = { "value" : aroon_osc , "type" : "float"}
                trend_list.append(aroonDict)

                trend_dict[market] = trend_list


            volume_keys = ["ad" , "obv"]
            volume_headers =  [{"key" : "indicator" , "name" : "Indicator"} ,
                                    {"key" : "value" , "name" : "Value"}]

            volume_dict = {}
            for summaryRow in latestTradeRows:
                market = summaryRow["market"]
                volume_list = []

                ad = summaryRow["ad"]
                adDict = {}
                adDict["indicator"] = { "value" : "ADX" , "type" : "string"}
                adDict["value"] =   { "value" : ad , "type" : "float"}
                volume_list.append(adDict)

                obv = summaryRow["obv"]
                obvDict = {}
                obvDict["indicator"] = {"value": "On Balance Volume", "type": "string"}
                obvDict["value"] = {"value": obv, "type": "float"}
                volume_list.append(obvDict)

                volume_dict[market] = volume_list


            momentum_keys = ["mfi" , "rsi"]
            momentum_headers =  [{"key" : "indicator" , "name" : "Indicator"} ,
                                    {"key" : "value" , "name" : "Value"}]

            momentum_dict = {}
            for summaryRow in latestTradeRows:
                market = summaryRow["market"]
                momentum_list = []

                mfi = summaryRow["mfi"]
                mfiDict = {}
                mfiDict["indicator"] = {"value": "Money Flow Index", "type": "string"}
                mfiDict["value"] = {"value": mfi, "type": "float"}
                momentum_list.append(mfiDict)

                rsi = summaryRow["rsi"]
                rsiDict = {}
                rsiDict["indicator"] = {"value": "Relative Strength Index", "type": "string"}
                rsiDict["value"] = {"value": rsi, "type": "float"}
                momentum_list.append(rsiDict)

                momentum_dict[market] = momentum_list





            volatility_keys = ["atr"]


            movingAverageKeys = [ "indicator" , "value" ]
            movingAverageHeaders = [{"key" : "indicator" , "name" : "Indicator"} ,
                                    {"key" : "value" , "name" : "Value"}]

            allMovingAverageList = []
            marketDict = {}
            chartsDict = {}
            markets =[]



            logger.info('Latest trade rows ' + str(len(latestTradeRows)) + ' ' + str(timeD.total_seconds()))

            sumStart = datetime.now()

            for summaryRow in latestTradeRows:

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

            sumEndDur = datetime.now() - startTime
            onlySumDur = datetime.now() - sumStart
            logger.info("Only sum " + str(onlySumDur.total_seconds()))
            logger.info("Sum end " + str(sumEndDur.total_seconds()))

            marketStart = datetime.now()

            for market in markets:

                marketsOHLCVs = [d for d in summaryRows if d["market"] == market]
                sortedOHLCVs = sorted(marketsOHLCVs , key = lambda k:k["starttime"])
                starttimes = []
                opens = []
                highs = []
                lows = []
                closes = []
                volumes = []

                for data in sortedOHLCVs:
                    starttimes.append(data["starttime"])
                    opens.append(data["open"])
                    highs.append(data["high"])
                    lows.append(data["low"])
                    closes.append(data["close"])
                    volumes.append(data["volume"])
                    chartsDict[market] = {}
                    chartsDict[market]["starttimes"] = starttimes
                    chartsDict[market]['opens'] = opens
                    chartsDict[market]["lows"] = lows
                    chartsDict[market]["highs"] = highs
                    chartsDict[market]["closes"] = closes
                    chartsDict[market]["volumes"] = volumes

            marketEnd = datetime.now() - startTime
            logger.info("Market " + str(marketEnd.total_seconds()))


            response["markets"] = markets
            response["results"] = summaryRows
            response["trend_data"] = trend_dict
            response["trend_headers"] = trend_headers
            response["volume_data"] = volume_dict
            response["volume_headers"] = volume_headers
            response["momentum_data"] = momentum_dict
            response["momentum_headers"] = momentum_headers
            response["movingaverages"] = marketDict
            response["movingaveragesheaders"] = movingAverageHeaders
            response["charts"] = chartsDict

            logger.info("Here " + str(marketEnd.total_seconds()))

        soLong = datetime.now() - startTime

        logger.info('soLong ' + str(soLong.total_seconds()))


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


        # Get price and volumes
        geckoPVKwargs = {}
        geckoPVKwargs["starttime"] = tradingStartTime


        price_vol_at_list = ["total_volume" ,"price_change_24h" , "current_price" , "high_24h" , "low_24h" , "price_change_percentage_24h",
                                                                "price_change_percentage_7d", "price_change_percentage_14d", "price_change_percentage_30d" , "price_change_percentage_60d" ,
                                                                "price_change_percentage_200d" , "price_change_percentage_1y" , "market_cap" , "market_cap_change_24h" ,
                                                                "market_cap_change_percentage_24h"]

        price_data_rows = Geckopricevolume.objects.filter(**geckoPVKwargs).values("coinid__name" , "coinid__symbol" , "total_volume" ,"price_change_24h" , "current_price" , "high_24h" , "low_24h" , "price_change_percentage_24h",
                                                                "price_change_percentage_7d", "price_change_percentage_14d", "price_change_percentage_30d" , "price_change_percentage_60d" ,
                                                                "price_change_percentage_200d" , "price_change_percentage_1y" , "market_cap" , "market_cap_change_24h" ,
                                                                "market_cap_change_percentage_24h")

        price_vol_keys = ["coinid__name" , "total_volume" , "price_change_24h" , "current_price" , "high_24h" ,"low_24h" , "market_cap" ,
                          "market_cap_change_24h" ,  "market_cap_change_percentage_24h"]
        price_vol_headers = [ {
            "key" : "coinid__name",
            "name" : "Coin" } ,
            {
                "key": "current_price",
                "name": "Current Price"
            },
            {
                "key" : "total_volume",
                "name" : "Total Volume"
            } ,
            {
                "key" : "price_change_24h",
                "name" : "Price Change (24h)"
            } ,

            {
                "key" : "high_24h",
                "name" : "High (24h)"
            } ,
            {
                "key" : "low_24h",
                "name" : "Low (24h)"
            } ,
            {
                "key" : "market_cap",
                "name" : "Market Cap"
            } ,
            {
                "key" : "market_cap_change_24h",
                "name" : "Market Cap Change (24h)"
            } ,
            {
                "key" : "market_cap_change_percentage_24h",
                "name" : "Market Cap Change % (24h)"
            }
        ]

        price_vol_list = []
        for price_data_row in price_data_rows:
            price_vol_column = {}
            for key in price_vol_keys:
                valType = "string"
                if key == "coinid__name":
                    valType = "link"
                    price_vol_column[key] = {"value": price_data_row[key], "type": valType,
                                       "link": "/coin/" + price_data_row["coinid__symbol"]}
                elif type(price_data_row[key]) is str:
                    valType = "string"
                    price_vol_column[key] = {"value": price_data_row[key], "type": valType}
                elif type(price_data_row[key]) is float:
                    valType = "float"
                    price_vol_column[key] = {"value": price_data_row[key], "type": valType}
                elif type(price_data_row[key]) is int:
                    valType = "int"
                    price_vol_column[key] = {"value": price_data_row[key], "type": valType}

            price_vol_list.append(price_vol_column)

        # For price change
        price_change_keys = ["coinid__name" ,  "current_price" , "price_change_percentage_24h", "price_change_percentage_7d", "price_change_percentage_14d", "price_change_percentage_30d" ,
                             "price_change_percentage_60d" , "price_change_percentage_200d" , "price_change_percentage_1y"]

        price_change_headers = [
            {
                "key": "coinid__name",
                "name": "Coin"
            },
            {
                "key": "current_price",
                "name": "Current Price"
            } ,
            {
                "key" : "price_change_percentage_24h" ,
                "name" : "Price Change % (24h)"
            } ,
            {
                "key": "price_change_percentage_7d",
                "name": "Price Change % (7 days)"
            },
            {
                "key": "price_change_percentage_14d",
                "name": "Price Change % (14 days)"
            },
            {
                "key": "price_change_percentage_30d",
                "name": "Price Change % (30 days)"
            },
            {
                "key": "price_change_percentage_60d",
                "name": "Price Change % (60 days)"
            },
            {
                "key": "price_change_percentage_200d",
                "name": "Price Change % (200 days)"
            },
            {
                "key": "price_change_percentage_1y",
                "name": "Price Change % (1 year)"
            }
        ]

        price_change_list =[]
        for price_data_row in price_data_rows:
            price_change_column = {}
            for key in price_change_keys:
                valType = "string"
                if key == "coinid__name":
                    valType = "link"
                    price_change_column[key] = {"value": price_data_row[key], "type": valType,
                                       "link": "/coin/" + price_data_row["coinid__symbol"]}
                elif type(price_data_row[key]) is str:
                    valType = "string"
                    price_change_column[key] = {"value": price_data_row[key], "type": valType}
                elif type(price_data_row[key]) is float:
                    valType = "float"
                    price_change_column[key] = {"value": price_data_row[key], "type": valType}
                elif type(price_data_row[key]) is int:
                    valType = "int"
                    price_change_column[key] = {"value": price_data_row[key], "type": valType}

            price_change_list.append(price_change_column)


        response["price_change_headers"] = price_change_headers
        response["price_change_data"] = price_change_list
        response["price_vol_headers"] = price_vol_headers
        response["price_vol_data"] = price_vol_list







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
