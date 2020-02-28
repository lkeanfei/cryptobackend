from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Hourlydata
from .models import Technicals , Tradingtime , Hourlydatacoinpair, Hourlydatatechnicalsview , Technicalsavailablecoinpairs, Technicalsavailablemarkets , Geckofundamentals , Geckofundamentalsview ,Geckopricevolume , Geckocoinpair
from .models import Hourlyforecast, Hourlyforcastaccuracy , Rolling48Hmetrics
from django.db.models import Q
from datetime import timedelta ,datetime
from statistics import mean, median
import itertools
from itertools import groupby
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
    def getTableData(headers , data_dict_list):

        row_list = []
        for data_dict in data_dict_list:
            rowDict = {}
            for header in headers:
                cellDict = {"value": data_dict[header["key"]], "type": Utils.getVarType(data_dict[header["key"]])}
                rowDict[header["key"]] = cellDict
            row_list.append(rowDict)

        return row_list



    @staticmethod
    def getStatistics(val_list , bin_size , bin_count=5):

        ret_dict = {}
        ret_dict["mean"] = mean(val_list)
        ret_dict["median"] = median(val_list)

        max_val = max(val_list)

        bin_start = 0

        bin_list = []
        while bin_start < max_val:
            bin_dict = {}
            bin_dict["start"] = bin_start
            bin_dict["end"] = bin_start + bin_size
            bin_dict["count"] = 0
            bin_list.append(bin_dict)
            bin_start = bin_start + bin_size

        for val in val_list:
            for bin in bin_list:
                if val >= bin["start"] and val < bin["end"]:
                    bin["count"] = bin["count"] + 1
                    break

        val_count = len(val_list)

        for bin in bin_list:
            bin["percentage"] = 100.0* bin["count"]/val_count

        # print("Min val is " + str(min_val))
        # print("Max val is " + str(max_val))
        # print("Bin count "+ str(len(bin_list)))
        ret_dict["valcount"] = len(val_list)
        ret_dict["bins"] = bin_list[:bin_count]

        return ret_dict

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
    def getVarType(var):

        if type(var) == str:
            return "string"

        else:
            return "float"




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

class ForecastSummaryView(APIView):

    def post(self, request):

        response = {}

        startTime = Utils.getTradingStartTime()
        coinpairMarketArgs = {}
        coinpairMarketArgs["starttime"] = startTime

        arguments = ["coinpair", "market", "prevstarttime", "mad", "mape", "nfm", "model_type", "starttime"]

        rows = Hourlyforcastaccuracy.objects.filter(**coinpairMarketArgs).values(*arguments)

        coinpairlist = list( set([row["coinpair"] for row in rows]))
        coinpairlist.sort()

        model_type_list = list(set( [row["model_type"] for row in rows] ))
        model_type_list.sort()

        # By model type
        mape_accuracy_dict = {}
        mape_dist_dict = {}
        for model_type in model_type_list:
            mape_group = [row["mape"] for row in rows if row["model_type"] == model_type]
            mape_dist = Utils.getStatistics(mape_group, 0.5)
            mape_accuracy_dict[model_type] = mape_group
            mape_dist_dict[model_type] = mape_dist

        #  sort by mad and mape
        sorted_mape_list = sorted(rows, key= lambda k:k["mape"])

        # response["coinpairlist"] = coinpairlist
        response["modeltypelist"] = model_type_list
        response["mapeaccuracytbymodel"] = mape_accuracy_dict
        response["mapedist"] = mape_dist_dict

        mapetableheaders =  [ {
                "key" : "market",
                "name" : "Market"
            } ,
                {
                    "key" : "coinpair",
                    "name" : "Bullish MAs"
                }
                ,
                {
                    "key": "mad",
                    "name": "MAD"
                }
                ,
                {
                    "key": "mape",
                    "name": "MAPE (%)"
                }
            ]

        inaccurate_mape_list = sorted(sorted_mape_list[-10:] , key= lambda k:k["mape"] , reverse=True)

        most_acc_mape_list = Utils.getTableData(mapetableheaders , sorted_mape_list[:10])
        most_inacc_mape_list = Utils.getTableData(mapetableheaders , inaccurate_mape_list)
        response["mapeheaders"] = mapetableheaders
        response["mostaccuratemape"] = most_acc_mape_list
        response["mostinaccuratemape"] = most_inacc_mape_list

        # Top volume at the hour




        return Response(response)

class ForecastView(APIView):

    def post(self, request):

        response = {}

        forecastheaders = [
            {
            "key": "model_type",
            "name": "Model"
            },
            {
                "key": "forecast_price",
                "name": "Forecast Price"
            }
            ,
            {
                "key": "price_diff",
                "name": "Price Difference"
            },
            {
                "key": "direction",
                "name": "Price Direction"
            },

        ]

        startTime = Utils.getTradingStartTime()
        print(startTime)

        # Technicals
        forecastKwargs = {}
        forecastKwargs['starttime'] = startTime
        forecastKwargs['coinpair'] = request.data['coinpair']
        forecastKwargs['market'] = request.data['market']

        forecastKeys = [d["key"] for d in forecastheaders]

        print(forecastKeys)

        forecastRows = Hourlyforecast.objects.filter(**forecastKwargs).values("starttime" , "model_type", "forecast_price" , "price_diff" , "direction" )

        forecaseDataList = []
        if len(forecastRows) == 0:
            forecastKwargs['starttime'] = startTime - timedelta(hours=1)
            startTime = startTime - timedelta(hours=1)
            forecastRows = Hourlyforecast.objects.filter(**forecastKwargs).values("starttime" , "model_type", "forecast_price",
                                                                                  "price_diff", "direction")


        for row in forecastRows:
            rowDict = {}

            for header in forecastheaders:
                cellDict = { "value" :  row[header["key"]] , "type" : Utils.getVarType(row[header["key"]])}
                rowDict[header["key"]] = cellDict

            forecaseDataList.append(rowDict)

        forecastStartTime = startTime + timedelta(hours=1)
        forecastEndTime = startTime + timedelta(hours=2)
        timerange = forecastStartTime.strftime("%Y-%m-%d %H:%M") + " - " + forecastEndTime.strftime("%H:%M")

        response["headers"] = forecastheaders
        response["data"] = forecaseDataList
        response["timerange"] = timerange



        return Response(response)




class AllCoinPairsView(APIView):

    def get(self, request):

        response = {}

        coinpair_rows = Hourlydata.objects.order_by('coinpair').values('coinpair').distinct()

        coinpair_list = []

        for coinpair in coinpair_rows:
            coinpair_list.append(coinpair['coinpair'])

        results_dict = {}

        for char_num in range(65,91):
            localcoin_list = [d for d in coinpair_list if d[0] == chr(char_num)]
            results_dict[chr(char_num)] = localcoin_list

        return Response(results_dict)

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


            fundamentalsFilter = {}
            fundamentalsFilter["starttime"] = tradingStartTime
            fundamentalsFilter["symbol"] = symbol

            fundamentals = Geckofundamentalsview.objects.filter(**fundamentalsFilter).values('coinid' ,'blocktime' , 'developer' , 'community' , 'liquidity' , 'publicinterest' , 'description' , 'small_img_url' , 'thumb_img_url' )


            geckoPriceVolumeKwargs = {}
            geckoPriceVolumeKwargs["starttime__lte"] = tradingStartTime
            geckoPriceVolumeKwargs["coinid__symbol"] = symbol
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

class CoinpairDetailsView(APIView):

    def __init__(self):

        self.data_headers = [{"key": "indicator", "name": "Indicator"},
                         {"key": "value", "name": "Value"}]


    def get_trend_list(self , summaryRow):

        trend_list = []

        sar = summaryRow["sar"]
        sarDict = {}
        sarDict["indicator"] = {"value": "Parabolic SAR", "type": "string"}
        sarDict["value"] = {"value": sar, "type": "float"}
        trend_list.append(sarDict)

        adx = summaryRow["adx"]
        adxDict = {}
        adxDict["indicator"] = {"value": "ADX", "type": "string"}
        adxDict["value"] = {"value": adx, "type": "float"}
        trend_list.append(adxDict)

        aroon_osc = summaryRow["aroonosc"]
        aroonDict = {}
        aroonDict["indicator"] = {"value": "Aroon Oscilator", "type": "string"}
        aroonDict["value"] = {"value": aroon_osc, "type": "float"}

        return trend_list

    def get_volume_list(self ,summaryRow):
        volume_list = []

        ad = summaryRow["ad"]
        adDict = {}
        adDict["indicator"] = {"value": "ADX", "type": "string"}
        adDict["value"] = {"value": ad, "type": "float"}
        volume_list.append(adDict)

        obv = summaryRow["obv"]
        obvDict = {}
        obvDict["indicator"] = {"value": "On Balance Volume", "type": "string"}
        obvDict["value"] = {"value": obv, "type": "float"}
        volume_list.append(obvDict)

        return volume_list

    def get_momentum_list(self , summaryRow):
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

        return momentum_list

    def get_movingaverage_list(self, summaryRow):

        marketMovAverageList = []

        marketMovingAverage = {}
        ema10 = summaryRow["ema10"]
        marketMovingAverage["indicator"] = {"value": "Exponential Moving Average(10)", "type": "string"}
        marketMovingAverage["value"] = {"value": ema10, "type": "float"}
        marketMovAverageList.append(marketMovingAverage)

        dema10 = summaryRow["dema10"]
        dema10dict = {}
        dema10dict["indicator"] = {"value": "Double Exponential Moving Average(10)", "type": "string"}
        dema10dict["value"] = {"value": dema10, "type": "float"}
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

        return marketMovAverageList

    def post(self, request):

        response = {}

        if "coinpair" in request.data.keys() and "market" in request.data.keys():
            print("technicals")
            coinpair = request.data["coinpair"]
            market = request.data["market"]

            tradingStartTime = Utils.getTradingStartTime()

            print("trading start time ")
            print(tradingStartTime)



            filterKwargs = {}
            filterKwargs["coinpair__iexact"] = coinpair
            filterKwargs["starttime"] = tradingStartTime
            filterKwargs["market"] = market

            summaryRows = Hourlydatatechnicalsview.objects.filter(**filterKwargs).values("starttime", "coinpair",
                                                                                         "market", "open", "high",
                                                                                         "low",
                                                                                         "close", "volume", "upperband",
                                                                                         "midband", "lowerband",
                                                                                         "dema10", "ema10", "sar",
                                                                                         "sma10", "wma10", "ad", "obv",
                                                                                         "atr", "adx", "aroonosc", "dx",
                                                                                         "macd", "macdsignal",
                                                                                         "macdhist", "mfi",
                                                                                         "dema20", "ema20", "sma20",
                                                                                         "wma20", "dema50", "ema50",
                                                                                         "sma50", "wma50",
                                                                                         "rsi", "pricechangepct",
                                                                                         "unusualvolume",
                                                                                         "macdindicator")


            if len(summaryRows) > 0 :
                summaryRow = summaryRows[0]
                momentum_data = self.get_momentum_list(summaryRow)
                ma_data = self.get_movingaverage_list(summaryRow)
                trend_data = self.get_trend_list(summaryRow)
                volume_data = self.get_volume_list(summaryRow)

                response["data_headers"] = self.data_headers
                response["momentum_data"] = momentum_data
                response["ma_data"] = ma_data
                response["trend_data"] = trend_data
                response["volume_data"] = volume_data



        return Response(response)



class CoinPairView(APIView):

    def post(self , request):
        response = {}

        startTime = datetime.now()

        if "coinpair" in request.data.keys():
            print("")
            coinpair = request.data["coinpair"]

            tradingStartTime = Utils.getTradingStartTime()

            print("trading start time " )
            print(tradingStartTime)

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
                print(summaryRow)
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

            print("markets are")
            print(markets)

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

        startLogTime = datetime.now()

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

        total_dur = datetime.now() - startLogTime

        print("Time taken is " + str(total_dur.total_seconds()))

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



        return Response({'message': 'HelloApiView 123'})

class HourlyForecastAccuracySummary(APIView):

    def post(self, request):
        # Given the trading start time , get the summary
        #  summary  that based on the coinpair ?
        #  for coinpair , get
        #  or the method , what is the histogram for the past 1 hour
        #  past 4 hours , past 8 hours , on all cryptos ?
        #  1 hour , 4 hour , 8 hour on given crypto

        print("")

class CoinPairRolling48hMetricsView(APIView):

    def post(self, request):

        response = {}

        if "coinpair" in request.data.keys() and "market" in request.data.keys():
            coinpair = request.data["coinpair"]
            market = request.data["market"]

            startTime = Utils.getTradingStartTime()
            past48hTime = startTime - timedelta(hours=48)

            rollingMetricsArgs = {}
            rollingMetricsArgs["starttime__gte"] = past48hTime
            rollingMetricsArgs["coinpair"] = coinpair
            rollingMetricsArgs["market"] = market

            arguments = ["coinpair", "market", "starttime", "model_type", "hits_pct", "diraccuracy_pct"]

            rows = Rolling48Hmetrics.objects.filter(**rollingMetricsArgs).values(*arguments)

            print("length oif rows " + str(len(rows)))

            # group by model types
            coinpairMarketDict = {}

            sorted_rows = sorted( rows, key= lambda x: x["model_type"])

            for key,value_dicts in itertools.groupby(sorted_rows , key=lambda x:x["model_type"]):
                print( key)
                sorted_list =sorted(value_dicts, key= lambda item: item["starttime"])

                sorted_datetime = [d["starttime"] for d in sorted_list]
                hits_pct_list = [d["hits_pct"] for d in sorted_list]
                diraccuracy_pct_list = [d["diraccuracy_pct"] for d in sorted_list]

                print("datetime list " + str(len(sorted_datetime)))
                print("len data " + str(len(hits_pct_list)))
                print("diraccuracy " + str(len(diraccuracy_pct_list)))
                coinpairMarketDict[key] = { "datetime_list" : sorted_datetime , "hits_pct_list" : hits_pct_list , "diraccuracy_pct_list" : diraccuracy_pct_list}

            response["results"] = coinpairMarketDict


        return Response(response)



class Rolling48hMetricsView(APIView):

    def post(self, request):

        response = {}

        startTime = Utils.getTradingStartTime()
        rollingMetricsArgs = {}
        rollingMetricsArgs["starttime"] = startTime
        arguments = ["coinpair", "market", "starttime" , "model_type" , "hits_pct" , "diraccuracy_pct"]

        rows = Rolling48Hmetrics.objects.filter(**rollingMetricsArgs).values(*arguments)

        sorted_hits_list = sorted(rows , key = lambda k:k["hits_pct"] )

        most_acc_hits = sorted_hits_list[:10]
        most_inacc_hits = sorted_hits_list[-10:]

        sorted_diracc_list = sorted(rows , key= lambda k:k["diraccuracy_pct"])
        most_acc_diracc = sorted_diracc_list[:10]
        most_inacc_diracc = sorted_diracc_list[-10:]

        hitstableheaders = [{
            "key": "market",
            "name": "Market"
        },
            {
                "key": "coinpair",
                "name": "Coinpair"
            }
            ,
            {
                "key": "model_type",
                "name": "Model"
            }
            ,
            {
                "key": "hits_pct",
                "name": "Hits (%)"
            }
        ]

        most_acc_hits_table_data = Utils.getTableData(hitstableheaders, most_acc_hits )
        most_inacc_hits_table_data =  Utils.getTableData( hitstableheaders , most_acc_hits)
        most_acc_diracc_table_data = Utils.getTableData(hitstableheaders , most_acc_diracc)
        most_inacc_diracc_table_data = Utils.getTableData(hitstableheaders, most_inacc_diracc)

        response["headers"] = hitstableheaders
        response["most_acc_hits"] = most_acc_hits_table_data
        response["most_inacc_hits"] = most_inacc_hits_table_data
        response["most_acc_diracc"] = most_acc_diracc_table_data
        response["most_inacc_diracc"] = most_inacc_diracc_table_data


        return Response(response)



class CoinPairMarketForecastAccuracyView(APIView):

    def post(self, request):

        response = {}
        #  given the coinpair , and the startTime
        # Get the Hourly forecast accuracy for coinpair
        # also get the history for the past 24 hours
        #  display it to table
        results = []
        if "coinpair" in request.data.keys() and "market" in request.data.keys():
            coinpair = request.data["coinpair"]
            market = request.data["market"]

            startTime = Utils.getTradingStartTime()
            past_48h_startTime = startTime - timedelta(hours=48)



            arguments = ["coinpair" , "market" , "prevstarttime" , "mad" , "mape" , "nfm" , "model_type" , "starttime" , "hit" , "directionaccuracy"]

            rows = Hourlyforcastaccuracy.objects.filter(**coinpairMarketArgs).values(*arguments)

            mape_list_dict = {}
            for key,value_dicts in itertools.groupby(rows , key= lambda x:x["model_type"]):
                    mape_list = []
                    for d in value_dicts:
                        mape_list.append(d["mape"])

                    mape_list_dict[key] = mape_list


            parsed_rows = []

            headers = [ {"key" : "model_type", "name" : "Model type"},
                        {"key" : "time_range" , "name" : "Forecast range (UTC)"},
                        {"key": "mad", "name": "MAD(Mean Absolute Deviation)"},
                       {"key": "mape", "name": "MAPE(Mean Absolute Percentage Error)" },
                       {"key" : "nfm" ,"name" : "Normalized Forecast Metric (Bias)"}]

            for row in rows:

                parsed_dict = {}
                for key in row.keys():

                    if key == "prevstarttime" or key == "starttime":
                        parsed_dict[key] = row[key].strftime("%Y-%m-%d %H:%M")
                        parsed_dict[key + "_val"] = row[key]
                    else:
                        parsed_dict[key] = row[key]

                parsed_rows.append(parsed_dict)

            table_rows = []
            for parsed_row in parsed_rows:

                table_row_dict = {}
                table_row_dict["startTime"] =parsed_row["prevstarttime_val"]
                time_range_start = parsed_row["prevstarttime_val"] + timedelta(hours=1)
                time_range_end = parsed_row["starttime_val"] + timedelta(hours=1)
                table_row_dict["time_range"] = { "value" : time_range_start.strftime("%Y-%m-%d %H:%M") + " - " + time_range_end.strftime("%H:%M") , "type" : "string"}
                for header in headers:

                    if header["key"] != "time_range":
                        print("header key is " + header["key"])
                        table_row_dict[header["key"]] = { "value" : parsed_row[header["key"]] , "type" : Utils.getVarType(parsed_row[header["key"]])}

                table_rows.append(table_row_dict)

            sorted_table_rows = sorted(table_rows , key= lambda k:k["startTime"] , reverse=True)

            response["data"] = sorted_table_rows
            response["headers"] = headers
            response["alldata"] = parsed_rows
            mape_stats_dict = {}

            for key in mape_list_dict:
                mape_stats_dict[key] = Utils.getStatistics(mape_list_dict[key] , 0.5)
            response["mape_stats"] = mape_stats_dict

            # For line charts datam
            mape_chart_dict = {}
            mad_chart_dict = {}
            for k,g in groupby(parsed_rows , lambda k:k["model_type"]):
                sorted_dict_list = sorted(g, key= lambda k: k["starttime_val"])
                x_list = [d["starttime"] for d in sorted_dict_list]
                mape_list = [d["mape"] for d in sorted_dict_list]
                mad_list =  [d["mad"] for d in sorted_dict_list]
                mape_chart_dict[k] = { "x" : x_list , "y" : mape_list}
                mad_chart_dict[k] = {"x" : x_list , "y" : mad_list}

            response["mape_charts"] = mape_chart_dict
            response["mad_charts"] = mad_chart_dict

            #     Rolling 24-hour hit accuracy
            rolling_length = 24
            hits_chart_dict = {}
            for k,g in groupby(parsed_rows , lambda k:k["model_type"]):
                sorted_dict_list = sorted(g, key= lambda k: k["starttime_val"])
                x_list = [d["starttime"] for d in sorted_dict_list]
                all_hit_list = [ d["hit"] for d in sorted_dict_list]
                all_directionAccuracy_list = [ d["directionaccuracy"] for d in sorted_dict_list]

                date_list = []
                hits_pct_list =[]

                for offset in range(0,15):

                    from_index = 0 -offset - rolling_length
                    to_index = 0-offset
                    print("all hit list " + str(len(all_hit_list)))
                    print("From " + str(from_index) + " to " + str(to_index))

                    if to_index == 0:
                        hit_list = all_hit_list[ from_index:]
                    else:
                        hit_list = all_hit_list[from_index: to_index]
                    hit_count = hit_list.count(1)
                    missed_count = hit_list.count(0)

                    hit_pct = 100.0* hit_count/ len(hit_list)

                    date_list.append(x_list[to_index-1])
                    hits_pct_list.append( hit_pct )
                    print(x_list[to_index-1])

                    print( "total leng" + str(len(hit_list)) + ".hits " + str(hit_count) + ". misses " + str(missed_count))
                    print("24 hour list length " + str(len(sorted_dict_list)))

                hits_chart_dict[k] = { "x" : date_list , "y" : hits_pct_list}

            response["hits_chart"] = hits_chart_dict

            # Rolling direction accuracy

        return Response(response)

class HourlyDataCoinpairView(APIView):

    def post(self, request):

        response = {}

        if "coinpair" in request.data.keys():

            hdcoinpairArgs = {}
            hdcoinpairArgs["coinpair"] = request.data["coinpair"]
            rows = Hourlydatacoinpair.objects.filter(**hdcoinpairArgs).values("market")

            coinpair_list= list(map(lambda x: x["market"] , rows))
            coinpair_list.sort()

            response["markets"]= coinpair_list

        return Response(response)
