from django.core.validators import MinValueValidator
from django.db import models
from django_extensions.db.fields import UUIDField


class Vendor(models.Model):
    vendor_id = UUIDField()
    name = models.CharField(max_length=60, blank=False, null=False)


class Activity(models.Model):
    activity_id = UUIDField()
    name = models.CharField(max_length=100, blank=False, null=False)
    vendor = models.ForeignKey(Vendor)


class ActivityInstance(models.Model):
    activity_instance_id = UUIDField()
    activity = models.ForeignKey(Activity)
    start_time = models.BigIntegerField(blank=False, null=False)
    end_time = models.BigIntegerField(blank=False, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField(blank=False, null=False, validators=[MinValueValidator(10)])
    bookings = models.IntegerField(default=0, blank=False, null=False)
