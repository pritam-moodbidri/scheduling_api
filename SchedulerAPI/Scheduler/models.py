from django.db import models
from django_extensions.db.fields import UUIDField


class Vendor(models.Model):
    guid = UUIDField()
    name = models.CharField(max_length=60, blank=False, null=False)


class Activity(models.Model):
    guid = UUIDField()
    name = models.CharField(max_length=100, blank=False, null=False)
    vendor = models.ForeignKey(Vendor)


class ActivityInstance(models.Model):
    guid = UUIDField()
    start_time = models.BigIntegerField(blank=False, null=False)
    end_time = models.BigIntegerField(blank=False, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField(blank=False, null=False)
    bookings = models.IntegerField(default=0, blank=False, null=False)

