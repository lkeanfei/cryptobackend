from django.db import models

# Create your models here.
class Coin(models.Model):
    name = models.CharField(max_length=45, blank=True, null=True)
    symbol = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'Coin'
        unique_together = (('id', 'symbol'),)


class Coinpair(models.Model):
    baseasset = models.CharField(db_column='baseAsset', max_length=45, blank=True, null=True)  # Field name made lowercase.
    quoteasset = models.CharField(db_column='quoteAsset', max_length=45, blank=True, null=True)  # Field name made lowercase.
    name = models.CharField(max_length=45, blank=True, null=True)
    market = models.ForeignKey('Market', models.DO_NOTHING, db_column='market', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'CoinPair'
        unique_together = (('market', 'name'),)


class Hourlydata(models.Model):
    id = models.BigAutoField(primary_key=True)
    open = models.FloatField(blank=True, null=True)
    high = models.FloatField(blank=True, null=True)
    low = models.FloatField(blank=True, null=True)
    close = models.FloatField(blank=True, null=True)
    volume = models.FloatField(blank=True, null=True)
    coinpair = models.ForeignKey(Coinpair, models.DO_NOTHING, db_column='coinpair', blank=True, null=True)
    market = models.ForeignKey('Market', models.DO_NOTHING, db_column='market', blank=True, null=True)
    starttime = models.DateTimeField(db_column='startTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'HourlyData'
        unique_together = (('market', 'starttime', 'coinpair'),)


class Market(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'Market'
        unique_together = (('id', 'name'),)


class Technicals(models.Model):
    coinpair = models.CharField(max_length=45, blank=True, null=True)
    exchange = models.CharField(max_length=45, blank=True, null=True)
    starttime = models.DateTimeField(db_column='startTime', blank=True, null=True)  # Field name made lowercase.
    upperband = models.FloatField(blank=True, null=True)
    midband = models.FloatField(blank=True, null=True)
    lowerband = models.FloatField(blank=True, null=True)
    dema10 = models.FloatField(blank=True, null=True)
    ema10 = models.FloatField(blank=True, null=True)
    sar = models.FloatField(blank=True, null=True)
    sma10 = models.FloatField(blank=True, null=True)
    wma10 = models.FloatField(blank=True, null=True)
    ad = models.FloatField(blank=True, null=True)
    obv = models.FloatField(blank=True, null=True)
    atr = models.FloatField(blank=True, null=True)
    adx = models.FloatField()
    aroonosc = models.FloatField(blank=True, null=True)
    dx = models.FloatField(blank=True, null=True)
    macd = models.FloatField(blank=True, null=True)
    macdsignal = models.FloatField(blank=True, null=True)
    macdhist = models.FloatField(blank=True, null=True)
    mfi = models.FloatField(blank=True, null=True)
    rsi = models.FloatField(blank=True, null=True)
    dema20 = models.FloatField(blank=True, null=True)
    ema20 = models.FloatField(blank=True, null=True)
    sma20 = models.FloatField(blank=True, null=True)
    wma20 = models.FloatField(blank=True, null=True)
    unusualvolume = models.FloatField(blank=True, null=True)
    pricechangepct = models.FloatField(blank=True, null=True)
    dema10bullish = models.IntegerField(blank=True, null=True)
    dema20bullish = models.IntegerField(blank=True, null=True)
    ema10bullish = models.IntegerField(blank=True, null=True)
    ema20bullish = models.IntegerField(blank=True, null=True)
    sma10bullish = models.IntegerField(blank=True, null=True)
    sma20bullish = models.IntegerField(blank=True, null=True)
    wma10bullish = models.IntegerField(blank=True, null=True)
    wma20bullish = models.IntegerField(blank=True, null=True)
    dema50 = models.FloatField(blank=True, null=True)
    dema50bullish = models.IntegerField(blank=True, null=True)
    sma50 = models.FloatField(blank=True, null=True)
    sma50bullish = models.IntegerField(blank=True, null=True)
    wma50 = models.FloatField(blank=True, null=True)
    wma50bullish = models.IntegerField(blank=True, null=True)
    ema50 = models.FloatField(blank=True, null=True)
    ema50bullish = models.IntegerField(blank=True, null=True)
    macdindicator = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'technicals'
        unique_together = (('id', 'adx'), ('exchange', 'coinpair', 'starttime'),)

class Technicalsavailablemarkets(models.Model):
    exchange = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'TechnicalsAvailableMarkets'

class Technicalsavailablecoinpairs(models.Model):
    coinpair = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'TechnicalsAvailableCoinPairs'

class Tradingtime(models.Model):
    exchange = models.CharField(max_length=45, blank=True, null=True)
    starttime = models.DateTimeField(db_column='startTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TradingTime'
