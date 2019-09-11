current C:\cryptobackend\cryptobackend
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Geckopricevolume(models.Model):
    total_volume = models.FloatField(blank=True, null=True)
    price_change_24h = models.FloatField(blank=True, null=True)
    current_price = models.FloatField(blank=True, null=True)
    high_24h = models.FloatField(blank=True, null=True)
    low_24h = models.FloatField(blank=True, null=True)
    price_change_percentage_24h = models.FloatField(blank=True, null=True)
    price_change_percentage_7d = models.FloatField(blank=True, null=True)
    price_change_percentage_14d = models.FloatField(blank=True, null=True)
    price_change_percentage_30d = models.FloatField(blank=True, null=True)
    price_change_percentage_60d = models.FloatField(blank=True, null=True)
    price_change_percentage_200d = models.FloatField(blank=True, null=True)
    price_change_percentage_1y = models.FloatField(blank=True, null=True)
    market_cap = models.BigIntegerField(blank=True, null=True)
    market_cap_change_24h = models.FloatField(blank=True, null=True)
    market_cap_change_percentage_24h = models.FloatField(blank=True, null=True)
    coinid = models.ForeignKey('Geckocoin', models.DO_NOTHING, db_column='coinid', blank=True, null=True)
    starttime = models.DateTimeField(db_column='startTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GeckoPriceVolume'
        unique_together = (('coinid', 'starttime'),)
