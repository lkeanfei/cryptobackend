current D:\cryptobackend\cryptobackend
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


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
    coinpair = models.ForeignKey(Coinpair, models.DO_NOTHING, db_column='coinpair', blank=True, null=True)
    market = models.CharField(max_length=45, blank=True, null=True)
    starttime = models.DateTimeField(db_column='startTime', blank=True, null=True)  # Field name made lowercase.
    upperband = models.FloatField(blank=True, null=True)
    midband = models.FloatField(blank=True, null=True)
    lowerband = models.FloatField(blank=True, null=True)
    dema30 = models.FloatField(blank=True, null=True)
    ema30 = models.FloatField(blank=True, null=True)
    sar = models.FloatField(blank=True, null=True)
    sma30 = models.FloatField(blank=True, null=True)
    wma30 = models.FloatField(blank=True, null=True)
    ad = models.FloatField(blank=True, null=True)
    obv = models.FloatField(blank=True, null=True)
    atr = models.FloatField(blank=True, null=True)
    adx = models.FloatField(blank=True, null=True)
    aroonosc = models.FloatField(blank=True, null=True)
    dx = models.FloatField(blank=True, null=True)
    macd = models.FloatField(blank=True, null=True)
    macdsignal = models.FloatField(blank=True, null=True)
    macdhist = models.FloatField(blank=True, null=True)
    mfi = models.FloatField(blank=True, null=True)
    rsi = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'technicals'
        unique_together = (('market', 'coinpair', 'starttime'),)
