import calendar
from datetime import datetime
import dateutil.parser
from django.shortcuts import get_object_or_404
from Scheduler.models import ActivityInstance, Activity


class ActivityInstanceManager:

    def retrieve_activity_instance(self, activity_instance_id):
        activity_instance_filter = ActivityInstance.objects.filter(activity_instance_id=activity_instance_id)
        if activity_instance_filter.count() is not 1:
            return None
        else:
            return activity_instance_filter[0]

    def update_activity_instance(self, activity_instance_id, **kwargs):
        activity_instance_filter = ActivityInstance.objects.filter(activity_instance_id=activity_instance_id)
        if activity_instance_filter.count() is not 1:
            return None
        else:
            activity_instance = activity_instance_filter[0]
            for field, value in kwargs.items():
                setattr(activity_instance, field, value)

            if activity_instance.capacity < 1:
                raise InvalidCapacityException(activity_instance.capacity)

            if activity_instance.capacity < activity_instance.bookings:
                raise BookingsCountInvalidException(activity_instance.capacity, activity_instance.bookings)

            if activity_instance.end_time < activity_instance.start_time or activity_instance.end_time \
                    - activity_instance.start_time < 1800:
                raise InvalidActivityInstanceDuration()

            activity_instance.save()
            return activity_instance

    def create_activity_instance(self, activity_id, start_time, end_time, price, capacity, bookings=0):
        activity = Activity.objects.filter(activity_id=activity_id)

        if activity.count() is not 1:
            raise InvalidActivityException(activity_id)

        if capacity < 1:
            raise InvalidCapacityException(capacity)

        if bookings > capacity:
            raise BookingsCountInvalidException(capacity, bookings)

        if end_time < start_time or end_time-start_time < 1800:
            raise InvalidActivityInstanceDuration()

        activity_instance = ActivityInstance(activity=activity[0],
                                             start_time=start_time,
                                             end_time=end_time,
                                             price=price,
                                             capacity=capacity,
                                             bookings=bookings)
        activity_instance.save()
        return activity_instance

    def delete_activity_instance(self, activity_instance_id):
        activity_instance_filter = ActivityInstance.objects.filter(activity_instance_id=activity_instance_id)
        if activity_instance_filter.count() is not 1:
            return False
        else:
            activity_instance_filter[0].delete()
            return True

class InvalidActivityException(Exception):
    def __init__(self, activity_id):
        super().__init__(self, "Invalid Activity with id %s" % activity_id)


class BookingsCountInvalidException(Exception):
    def __init__(self, capacity, bookings):
        super().__init__(self, "Tried to make %s bookings with capacity of %s" % (bookings, capacity))


class InvalidCapacityException(Exception):
    def __init__(self, capacity):
        super().__init__(self, "Invalid capacity of %s" % capacity)


class InvalidActivityInstanceDuration(Exception):
    def __init__(self):
        super().__init__(self, "The duration of the activity is less than 30 minutes.")


