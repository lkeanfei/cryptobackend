current D:\cryptobackend\cryptobackend
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Technicals(models.Model):
    coinpair = models.ForeignKey('Coinpair', models.DO_NOTHING, db_column='coinpair', blank=True, null=True)
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

    class Meta:
        managed = False
        db_table = 'technicals'
        unique_together = (('id', 'adx'), ('exchange', 'coinpair', 'starttime'),)
