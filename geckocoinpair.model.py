current C:\cryptobackend\cryptobackend
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Geckocoinpair(models.Model):
    coin = models.CharField(max_length=45, blank=True, null=True)
    coinpair = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'GeckoCoinPair'
        unique_together = (('coin', 'coinpair'),)
