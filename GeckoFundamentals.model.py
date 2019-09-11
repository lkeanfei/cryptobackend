current C:\cryptobackend\cryptobackend
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Geckofundamentals(models.Model):
    coinid = models.ForeignKey('Geckocoin', models.DO_NOTHING, db_column='coinid', blank=True, null=True)
    blocktime = models.IntegerField(db_column='BlockTime', blank=True, null=True)  # Field name made lowercase.
    developer = models.FloatField(db_column='Developer', blank=True, null=True)  # Field name made lowercase.
    community = models.FloatField(db_column='Community', blank=True, null=True)  # Field name made lowercase.
    liquidity = models.FloatField(db_column='Liquidity', blank=True, null=True)  # Field name made lowercase.
    publicinterest = models.FloatField(db_column='PublicInterest', blank=True, null=True)  # Field name made lowercase.
    starttime = models.DateTimeField(db_column='startTime', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GeckoFundamentals'
        unique_together = (('coinid', 'starttime'),)
