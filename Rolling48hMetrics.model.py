current D:\cryptobackend\cryptobackend
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Rolling48Hmetrics(models.Model):
    market = models.CharField(max_length=45, blank=True, null=True)
    coinpair = models.CharField(max_length=45, blank=True, null=True)
    model_type = models.CharField(max_length=45, blank=True, null=True)
    hits_pct = models.FloatField(blank=True, null=True)
    diraccuracy_pct = models.FloatField(db_column='dirAccuracy_pct', blank=True, null=True)  # Field name made lowercase.
    starttime = models.DateTimeField(db_column='startTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Rolling48hMetrics'
        unique_together = (('starttime', 'market', 'coinpair', 'model_type'),)
