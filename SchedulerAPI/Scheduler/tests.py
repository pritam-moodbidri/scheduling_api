from datetime import datetime
import json
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test import TestCase
import pytz
from Scheduler.models import Vendor, Activity, ActivityInstance
from Scheduler.activity_instance_manager import ActivityInstanceManager, InvalidActivityException, BookingsCountInvalidException, InvalidCapacityException
from SchedulerAPI import util


class ScheduleViewTest(TestCase):
    def test_get_activity_instance(self):
        vendor1 = create_vendor('vendor1')
        activity1 = create_activity('activity1', vendor1)
        activity2 = create_activity('activity2', vendor1)

        start_time = datetime.now(tz=pytz.timezone('Australia/Sydney')).replace(hour=3, minute=30, month=1)
        end_time = datetime.now(tz=pytz.timezone('Australia/Sydney')).replace(hour=4, minute=0, month=1)
        activity1_instance = ActivityInstance(activity=activity1,
                                              start_time=util.iso8601_to_utc_timestamp(start_time.isoformat('T')),
                                              end_time=util.iso8601_to_utc_timestamp(end_time.isoformat('T')),
                                              price=12.12, capacity=10, bookings=0)
        activity1_instance.save()
        activity2_instance = ActivityInstance(activity=activity2,
                                              start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('US/Eastern')).replace(hour=8, month=6).isoformat('T')),
                                              end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('US/Eastern')).replace(hour=15, month=6).isoformat('T')),
                                              price=12.12, capacity=10, bookings=4)
        activity2_instance.save()

        retrieved_activity1_instance = json.loads(self.client.get(reverse('activity_instance_view',
                                                                          args=[activity1_instance.activity_instance_id])).content.decode('utf-8'))

        self.assertIsNotNone(retrieved_activity1_instance['activity_instance_id'])
        self.assertEqual(util.iso8601_to_utc_timestamp(retrieved_activity1_instance['start_time']),
                         util.iso8601_to_utc_timestamp(start_time.isoformat('T')))
        self.assertEqual(util.iso8601_to_utc_timestamp(retrieved_activity1_instance['end_time']),
                         util.iso8601_to_utc_timestamp(end_time.isoformat('T')))

        retrieved_activity2_instance = json.loads(self.client.get(reverse('activity_instance_view',
                                                                          args=[activity2_instance.activity_instance_id])).content.decode('utf-8'))
        self.assertIsNotNone(retrieved_activity2_instance['activity_instance_id'])

        self.assertEqual(self.client.get(reverse('activity_instance_view', args=["0"])).status_code, 404)
        self.assertEqual(self.client.get(reverse('activity_instance_view', args=[""])).status_code, 404)
        self.assertEqual(self.client.get(reverse('activity_instance_view', args=[None])).status_code, 404)

    def test_put_activity_instance(self):
        vendor1 = create_vendor('vendor1')
        activity1 = create_activity('activity1', vendor1)
        activity_instance1 = ActivityInstance(activity=activity1,
                                              start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Hongkong')).replace(hour=14, month=7).isoformat('T')),
                                              end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Hongkong')).replace(hour=15, month=7).isoformat('T')),
                                              price=12.12, capacity=10, bookings=0)
        activity_instance1.save()

        activity_instance1 = json.loads(self.client.put(reverse('activity_instance_view',
                                                                args=[activity_instance1.activity_instance_id]),
                                                        {'start_time': datetime.now(tz=pytz.timezone('Asia/Kolkata')).replace(hour=1).isoformat('T')}).content.decode('utf-8'))
        retrieved_instance1 = ActivityInstance.objects.get(activity_instance_id=activity_instance1['activity_instance_id'])
        self.assertEqual(util.iso8601_to_utc_timestamp(activity_instance1['start_time']), retrieved_instance1.start_time)

        activity_instance1 = json.loads(self.client.put(reverse('activity_instance_view',
                                                                args=[activity_instance1['activity_instance_id']]),
                                                        {'end_time': datetime.now(tz=pytz.timezone('Greenwich')).replace(hour=14).isoformat('T')}).content.decode('utf-8'))
        retrieved_instance1 = ActivityInstance.objects.get(activity_instance_id=activity_instance1['activity_instance_id'])
        self.assertEqual(util.iso8601_to_utc_timestamp(activity_instance1['end_time']), retrieved_instance1.end_time)

        activity_instance1 = json.loads(self.client.put(reverse('activity_instance_view',
                                                                args=[activity_instance1['activity_instance_id']]),
                                                        {'price': 15.23}).content.decode('utf-8'))
        retrieved_instance1 = ActivityInstance.objects.get(activity_instance_id=activity_instance1['activity_instance_id'])
        self.assertEqual(float(activity_instance1['price']), float(retrieved_instance1.price))

        activity_instance1 = json.loads(self.client.put(reverse('activity_instance_view',
                                                                args=[activity_instance1['activity_instance_id']]),
                                                        {'capacity': 20}).content.decode('utf-8'))
        retrieved_instance1 = ActivityInstance.objects.get(activity_instance_id=activity_instance1['activity_instance_id'])
        self.assertEqual(int(activity_instance1['capacity']), retrieved_instance1.capacity)

        activity_instance1 = json.loads(self.client.put(reverse('activity_instance_view',
                                                                args=[activity_instance1['activity_instance_id']]),
                                                        {'bookings': 10}).content.decode('utf-8'))
        retrieved_instance1 = ActivityInstance.objects.get(activity_instance_id=activity_instance1['activity_instance_id'])
        self.assertEqual(int(activity_instance1['bookings']), retrieved_instance1.bookings)

        activity_instance1 = json.loads(self.client.put(reverse('activity_instance_view',
                                                                args=[activity_instance1['activity_instance_id']]),
                                                        {'bookings': 15,
                                                         'capacity': 25,
                                                         'start_time': datetime.now(tz=pytz.timezone('Iran')).replace(hour=2, month=9).isoformat('T'),
                                                         'end_time': datetime.now(tz=pytz.timezone('Turkey')).replace(hour=4, month=9).isoformat('T'),
                                                         'price': 300}).content.decode('utf-8'))
        retrieved_instance1 = ActivityInstance.objects.get(activity_instance_id=activity_instance1['activity_instance_id'])
        self.assertEqual(int(activity_instance1['bookings']), retrieved_instance1.bookings)
        self.assertEqual(int(activity_instance1['capacity']), retrieved_instance1.capacity)
        self.assertEqual(util.iso8601_to_utc_timestamp(activity_instance1['start_time']), retrieved_instance1.start_time)
        self.assertEqual(util.iso8601_to_utc_timestamp(activity_instance1['end_time']), retrieved_instance1.end_time)
        self.assertEqual(int(activity_instance1['price']), float(retrieved_instance1.price))

        with self.assertRaises(BookingsCountInvalidException):
            activity_instance1 = json.loads(self.client.put(reverse('activity_instance_view',
                                                                    args=[activity_instance1['activity_instance_id']]),
                                                            {'bookings': 30}).content.decode('utf-8'))

        with self.assertRaises(BookingsCountInvalidException):
            activity_instance1 = json.loads(self.client.put(reverse('activity_instance_view',
                                                                    args=[activity_instance1['activity_instance_id']]),
                                                            {'capacity': 100,
                                                             'bookings': 500}).content.decode('utf-8'))

        with self.assertRaises(BookingsCountInvalidException):
            activity_instance1 = json.loads(self.client.put(reverse('activity_instance_view',
                                                                    args=[activity_instance1['activity_instance_id']]),
                                                            {'bookings': 1100,
                                                             'capacity': 200}).content.decode('utf-8'))

        try:
            activity_instance1 = json.loads(self.client.put(reverse('activity_instance_view',
                                                                    args=[activity_instance1['activity_instance_id']]),
                                                            {'bookings': 1,
                                                             'capacity': 1}).content.decode('utf-8'))
        except BookingsCountInvalidException:
            self.fail("Equal capacity and bookings value raised exception.")

        with self.assertRaises(InvalidCapacityException):
            activity_instance1 = json.loads(self.client.put(reverse('activity_instance_view',
                                                                    args=[activity_instance1['activity_instance_id']]),
                                                            {'capacity': 0}).content.decode('utf-8'))

        with self.assertRaises(InvalidCapacityException):
            activity_instance1 = json.loads(self.client.put(reverse('activity_instance_view',
                                                                    args=[activity_instance1['activity_instance_id']]),
                                                            {'capacity': 0,
                                                             'bookings': 12}).content.decode('utf-8'))

        with self.assertRaises(InvalidCapacityException):
            activity_instance1 = json.loads(self.client.put(reverse('activity_instance_view',
                                                                    args=[activity_instance1['activity_instance_id']]),
                                                            {'capacity': -1}).content.decode('utf-8'))

    def test_post_activity_instance(self):
        vendor1 = create_vendor('vendor1')
        activity1 = create_activity('activity1', vendor1)
        activity_instance1 = json.loads(self.client.post(reverse('activity_instance_view', args=['']),
                                                         {'activity_id': activity1.activity_id,
                                                          'start_time': datetime.now(tz=pytz.timezone('Australia/Sydney')).replace(hour=3, minute=0, month=3).isoformat('T'),
                                                          'end_time': datetime.now(tz=pytz.timezone('Australia/Sydney')).replace(hour=3, minute=45, month=3).isoformat('T'),
                                                          'price': 12.12, 'capacity': 10,
                                                          'bookings': 0}).content.decode('utf-8'))
        self.assertIsNotNone(activity_instance1['activity_instance_id'])

        activity_instance2 = json.loads(self.client.post(reverse('activity_instance_view', args=['']),
                                                         {'activity_id': activity1.activity_id,
                                                          'start_time': datetime.now(tz=pytz.timezone('US/Eastern')).replace(hour=6, year=2025).isoformat('T'),
                                                          'end_time': datetime.now(tz=pytz.timezone('US/Eastern')).replace(hour=7, year=2025).isoformat('T'),
                                                          'price': 12.12,
                                                          'capacity': 10}).content.decode('utf-8'))
        self.assertIsNotNone(activity_instance2['activity_instance_id'])

        self.assertIsNotNone(activity_instance1)
        activity_instance3 = json.loads(self.client.post(reverse('activity_instance_view', args=['']),
                                                         {'activity_id': activity1.activity_id,
                                                          'start_time': datetime.now(tz=pytz.timezone('Europe/Warsaw')).replace(hour=4, month=12).isoformat('T'),
                                                          'end_time': datetime.now(tz=pytz.timezone('Europe/Warsaw')).replace(hour=10, month=12).isoformat('T'),
                                                          'price': 12.12, 'capacity': 10,
                                                          'bookings': 5}).content.decode('utf-8'))
        self.assertIsNotNone(activity_instance3['activity_instance_id'])

        self.assertIsNotNone(ActivityInstance.objects.get(activity_instance_id=activity_instance1['activity_instance_id']))
        self.assertIsNotNone(ActivityInstance.objects.get(activity_instance_id=activity_instance2['activity_instance_id']))

        with self.assertRaises(InvalidActivityException):
            activity_instance4 = json.loads(self.client.post(reverse('activity_instance_view', args=['']),
                                                             {'activity_id': None,
                                                              'start_time': datetime.now(tz=pytz.timezone('GMT')).replace(hour=1, year=2030).isoformat('T'),
                                                              'end_time': datetime.now(tz=pytz.timezone('GMT')).replace(hour=15, year=2030).isoformat('T'),
                                                              'price': 12.12, 'capacity': 10,
                                                              'bookings': 0}).content.decode('utf-8'))

        with self.assertRaises(InvalidActivityException):
            activity_instance5 = json.loads(self.client.post(reverse('activity_instance_view', args=['']),
                                                             {'activity_id': '',
                                                              'start_time': datetime.now(tz=pytz.timezone('Jamaica')).replace(hour=1, minute=15, month=5).isoformat('T'),
                                                              'end_time': datetime.now(tz=pytz.timezone('Jamaica')).replace(hour=6, month=5).isoformat('T'),
                                                              'price': 12.12, 'capacity': 10,
                                                              'bookings': 0}).content.decode('utf-8'))

        with self.assertRaises(InvalidActivityException):
            activity_instance6 = json.loads(self.client.post(reverse('activity_instance_view', args=['']),
                                                             {'activity_id': '0',
                                                              'start_time': datetime.now(tz=pytz.timezone('Asia/Tokyo')).replace(hour=4).isoformat('T'),
                                                              'end_time': datetime.now(tz=pytz.timezone('Asia/Tokyo')).replace(hour=9).isoformat('T'),
                                                              'price': 12.12, 'capacity': 10,
                                                              'bookings': 0}).content.decode('utf-8'))

        with self.assertRaises(BookingsCountInvalidException):
            activity_instance7 = json.loads(self.client.post(reverse('activity_instance_view', args=['']),
                                                             {'activity_id': activity1.activity_id,
                                                              'start_time': datetime.now(tz=pytz.timezone('Poland')).replace(hour=13, month=7).isoformat('T'),
                                                              'end_time': datetime.now(tz=pytz.timezone('Poland')).replace(hour=15, month=7).isoformat('T'),
                                                              'price': 12.12, 'capacity': 10,
                                                              'bookings': 11}).content.decode('utf-8'))

        with self.assertRaises(InvalidCapacityException):
            activity_instance8 = json.loads(self.client.post(reverse('activity_instance_view', args=['']),
                                                             {'activity_id': activity1.activity_id,
                                                              'start_time': datetime.now(tz=pytz.timezone('Pacific/Fiji')).replace(hour=17).isoformat('T'),
                                                              'end_time': datetime.now(tz=pytz.timezone('Pacific/Fiji')).replace(hour=19).isoformat('T'),
                                                              'price': 12.12,
                                                              'capacity': 0}).content.decode('utf-8'))

    def test_delete_activity_instance(self):
        vendor1 = create_vendor('vendor1')
        activity1 = create_activity('activity1', vendor1)
        activity2 = create_activity('activity2', vendor1)
        activity3 = create_activity('activity3', vendor1)

        activity1_instance1 = ActivityInstance(activity=activity1,
                                               start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Australia/Sydney')).replace(hour=12).isoformat('T')),
                                               end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Australia/Sydney')).replace(hour=14).isoformat('T')),
                                               price=12.12, capacity=10, bookings=0)
        activity1_instance1.save()

        activity1_instance2 = ActivityInstance(activity=activity1,
                                               start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('US/Eastern')).replace(hour=13, month=11).isoformat('T')),
                                               end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('US/Eastern')).replace(hour=17, month=11).isoformat('T')),
                                               price=12.12, capacity=10, bookings=0)
        activity1_instance2.save()

        activity2_instance1 = ActivityInstance(activity=activity2,
                                               start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Europe/Warsaw')).replace(hour=11).isoformat('T')),
                                               end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Europe/Warsaw')).replace(hour=14).isoformat('T')),
                                               price=12.12, capacity=10, bookings=0)
        activity2_instance1.save()

        activity2_instance2 = ActivityInstance(activity=activity2,
                                               start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Canada/Mountain')).replace(hour=1, month=4).isoformat('T')),
                                               end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Canada/Mountain')).replace(hour=2, month=4).isoformat('T')),
                                               price=12.12, capacity=10, bookings=0)
        activity2_instance2.save()

        activity3_instance1 = ActivityInstance(activity=activity3,
                                               start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Europe/Berlin')).replace(hour=1, minute=0).isoformat('T')),
                                               end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Europe/Berlin')).replace(hour=1, minute=30).isoformat('T')),
                                               price=12.12, capacity=10, bookings=0)
        activity3_instance1.save()

        activity3_instance2 = ActivityInstance(activity=activity3,
                                               start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Brazil/West')).replace(hour=15, minute=0, month=2).isoformat('T')),
                                               end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Brazil/West')).replace(hour=15, minute=45, month=2).isoformat('T')),
                                               price=12.12, capacity=10, bookings=0)
        activity3_instance2.save()

        self.assertEqual(self.client.delete(reverse('activity_instance_view',
                                                    args=[activity1_instance1.activity_instance_id])).status_code, 200)
        self.assertEqual(ActivityInstance.objects.filter(
            activity_instance_id=activity1_instance1.activity_instance_id).count(), 0)

        self.assertEqual(self.client.delete(reverse('activity_instance_view',
                                                    args=[activity1_instance2.activity_instance_id])).status_code, 200)
        self.assertEqual(ActivityInstance.objects.filter(
            activity_instance_id=activity1_instance2.activity_instance_id).count(), 0)

        delete_activity(activity2)

        self.assertEqual(ActivityInstance.objects.filter(
            activity_instance_id=activity2_instance1.activity_instance_id).count(), 0)
        self.assertEqual(ActivityInstance.objects.filter(
            activity_instance_id=activity2_instance2.activity_instance_id).count(), 0)

        delete_vendor(vendor1)

        self.assertEqual(Activity.objects.filter(activity_id=activity1.activity_id).count(), 0)
        self.assertEqual(Activity.objects.filter(activity_id=activity2.activity_id).count(), 0)
        self.assertEqual(Activity.objects.filter(activity_id=activity3.activity_id).count(), 0)

        self.assertEqual(ActivityInstance.objects.filter(
            activity_instance_id=activity3_instance1.activity_instance_id).count(), 0)
        self.assertEqual(ActivityInstance.objects.filter(
            activity_instance_id=activity3_instance2.activity_instance_id).count(), 0)

        self.assertEqual(self.client.delete(reverse('activity_instance_view',
                                                    args=[activity1_instance1.activity_instance_id])).status_code, 404)
        self.assertEqual(self.client.delete(reverse('activity_instance_view',
                                                    args=[activity1_instance2.activity_instance_id])).status_code, 404)


class SchedulingManagerTest(TestCase):

    def test_activity_instance_creation(self):
        scheduling_manager = ActivityInstanceManager()
        vendor1 = create_vendor('vendor1')
        activity1 = create_activity('activity1', vendor1)
        activity_instance1 = scheduling_manager.create_activity_instance(activity1.activity_id,
                                                                         util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Australia/Sydney')).replace(hour=3, minute=0, month=3).isoformat('T')),
                                                                         util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Australia/Sydney')).replace(hour=3, minute=45, month=3).isoformat('T')),
                                                                         12.12, 10, 0)
        self.assertIsNotNone(activity_instance1)
        activity_instance2 = scheduling_manager.create_activity_instance(activity1.activity_id,
                                                                         util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('US/Eastern')).replace(hour=6, year=2025).isoformat('T')),
                                                                         util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('US/Eastern')).replace(hour=7, year=2025).isoformat('T')),
                                                                         12.12, 1)
        self.assertIsNotNone(activity_instance2)

        self.assertIsNotNone(activity_instance1)
        activity_instance3 = scheduling_manager.create_activity_instance(activity1.activity_id,
                                                                         util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Europe/Warsaw')).replace(hour=4, month=12).isoformat('T')),
                                                                         util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Europe/Warsaw')).replace(hour=10, month=12).isoformat('T')),
                                                                         12.12, 10, 5)
        self.assertIsNotNone(activity_instance3)

        self.assertIsNotNone(ActivityInstance.objects.get(activity_instance_id=activity_instance1.activity_instance_id))
        self.assertIsNotNone(ActivityInstance.objects.get(activity_instance_id=activity_instance2.activity_instance_id))

        with self.assertRaises(InvalidActivityException):
            activity_instance4 = scheduling_manager.create_activity_instance(None,
                                                                             util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('GMT')).replace(hour=1, year=2030).isoformat('T')),
                                                                             util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('GMT')).replace(hour=15, year=2030).isoformat('T')),
                                                                             12.12, 10, 0)

        with self.assertRaises(InvalidActivityException):
            activity_instance5 = scheduling_manager.create_activity_instance("", util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Jamaica')).replace(hour=1, minute=15, month=5).isoformat('T')),
                                                                             util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Jamaica')).replace(hour=6, month=5).isoformat('T')),
                                                                             12.12, 10, 0)

        with self.assertRaises(InvalidActivityException):
            activity_instance6 = scheduling_manager.create_activity_instance("0", util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Asia/Tokyo')).replace(hour=4).isoformat('T')),
                                                                             util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Asia/Tokyo')).replace(hour=9).isoformat('T')),
                                                                             12.12, 10, 0)

        with self.assertRaises(BookingsCountInvalidException):
            activity_instance7 = scheduling_manager.create_activity_instance(activity1.activity_id,
                                                                             util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Poland')).replace(hour=13, month=7).isoformat('T')),
                                                                             util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Poland')).replace(hour=15, month=7).isoformat('T')),
                                                                             12.12, 10, 11)

        with self.assertRaises(InvalidCapacityException):
            activity_instance8 = scheduling_manager.create_activity_instance(activity1.activity_id,
                                                                             util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Pacific/Fiji')).replace(hour=17).isoformat('T')),
                                                                             util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Pacific/Fiji')).replace(hour=19).isoformat('T')),
                                                                             12.12, 0)

    def test_activity_instance_deletion(self):
        scheduling_manager = ActivityInstanceManager()
        vendor1 = create_vendor('vendor1')
        activity1 = create_activity('activity1', vendor1)
        activity2 = create_activity('activity2', vendor1)
        activity3 = create_activity('activity3', vendor1)

        activity1_instance1 = ActivityInstance(activity=activity1,
                                               start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Australia/Sydney')).replace(hour=12).isoformat('T')),
                                               end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Australia/Sydney')).replace(hour=14).isoformat('T')),
                                               price=12.12, capacity=10, bookings=0)
        activity1_instance1.save()

        activity1_instance2 = ActivityInstance(activity=activity1,
                                               start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('US/Eastern')).replace(hour=13, month=11).isoformat('T')),
                                               end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('US/Eastern')).replace(hour=17, month=11).isoformat('T')),
                                               price=12.12, capacity=10, bookings=0)
        activity1_instance2.save()

        activity2_instance1 = ActivityInstance(activity=activity2,
                                               start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Europe/Warsaw')).replace(hour=11).isoformat('T')),
                                               end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Europe/Warsaw')).replace(hour=14).isoformat('T')),
                                               price=12.12, capacity=10, bookings=0)
        activity2_instance1.save()

        activity2_instance2 = ActivityInstance(activity=activity2,
                                               start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Canada/Mountain')).replace(hour=1, month=4).isoformat('T')),
                                               end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Canada/Mountain')).replace(hour=2, month=4).isoformat('T')),
                                               price=12.12, capacity=10, bookings=0)
        activity2_instance2.save()

        activity3_instance1 = ActivityInstance(activity=activity3,
                                               start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Europe/Berlin')).replace(hour=1, minute=0).isoformat('T')),
                                               end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Europe/Berlin')).replace(hour=1, minute=30).isoformat('T')),
                                               price=12.12, capacity=10, bookings=0)
        activity3_instance1.save()

        activity3_instance2 = ActivityInstance(activity=activity3,
                                               start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Brazil/West')).replace(hour=15, minute=0, month=2).isoformat('T')),
                                               end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Brazil/West')).replace(hour=15, minute=45, month=2).isoformat('T')),
                                               price=12.12, capacity=10, bookings=0)
        activity3_instance2.save()

        self.assertTrue(scheduling_manager.delete_activity_instance(activity1_instance1.activity_instance_id))
        self.assertEqual(ActivityInstance.objects.filter(
            activity_instance_id=activity1_instance1.activity_instance_id).count(), 0)

        self.assertTrue(scheduling_manager.delete_activity_instance(activity1_instance2.activity_instance_id))
        self.assertEqual(ActivityInstance.objects.filter(
            activity_instance_id=activity1_instance2.activity_instance_id).count(), 0)

        delete_activity(activity2)

        self.assertEqual(ActivityInstance.objects.filter(
            activity_instance_id=activity2_instance1.activity_instance_id).count(), 0)
        self.assertEqual(ActivityInstance.objects.filter(
            activity_instance_id=activity2_instance2.activity_instance_id).count(), 0)

        delete_vendor(vendor1)

        self.assertEqual(Activity.objects.filter(activity_id=activity1.activity_id).count(), 0)
        self.assertEqual(Activity.objects.filter(activity_id=activity2.activity_id).count(), 0)
        self.assertEqual(Activity.objects.filter(activity_id=activity3.activity_id).count(), 0)

        self.assertEqual(ActivityInstance.objects.filter(
            activity_instance_id=activity3_instance1.activity_instance_id).count(), 0)
        self.assertEqual(ActivityInstance.objects.filter(
            activity_instance_id=activity3_instance2.activity_instance_id).count(), 0)

        self.assertFalse(scheduling_manager.delete_activity_instance(activity1_instance1.activity_instance_id))
        self.assertFalse(scheduling_manager.delete_activity_instance(activity1_instance2.activity_instance_id))

    def test_activity_instance_retrieval(self):
        scheduling_manager = ActivityInstanceManager()
        vendor1 = create_vendor('vendor1')
        activity1 = create_activity('activity1', vendor1)
        activity2 = create_activity('activity2', vendor1)

        activity1_instance = ActivityInstance(activity=activity1,
                                              start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Australia/Sydney')).replace(hour=3, minute=30, month=1).isoformat('T')),
                                              end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Australia/Sydney')).replace(hour=4, minute=0, month=1).isoformat('T')),
                                              price=12.12, capacity=10, bookings=0)
        activity1_instance.save()
        activity2_instance = ActivityInstance(activity=activity2,
                                              start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('US/Eastern')).replace(hour=8, month=6).isoformat('T')),
                                              end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('US/Eastern')).replace(hour=15, month=6).isoformat('T')),
                                              price=12.12, capacity=10, bookings=4)
        activity2_instance.save()

        retrieved_activity1_instance = scheduling_manager.retrieve_activity_instance(
            activity1_instance.activity_instance_id)
        self.assertIsNotNone(retrieved_activity1_instance)

        retrieved_activity2_instance = scheduling_manager.retrieve_activity_instance(
            activity2_instance.activity_instance_id)
        self.assertIsNotNone(retrieved_activity2_instance)

        self.assertIsNone(scheduling_manager.retrieve_activity_instance("0"))
        self.assertIsNone(scheduling_manager.retrieve_activity_instance(""))
        self.assertIsNone(scheduling_manager.retrieve_activity_instance(None))

    def test_activity_instance_update(self):
        scheduling_manager = ActivityInstanceManager()
        vendor1 = create_vendor('vendor1')
        activity1 = create_activity('activity1', vendor1)
        activity_instance1 = ActivityInstance(activity=activity1,
                                              start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Hongkong')).replace(hour=14, month=7).isoformat('T')),
                                              end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Hongkong')).replace(hour=15, month=7).isoformat('T')),
                                              price=12.12, capacity=10, bookings=0)
        activity_instance1.save()

        activity_instance1 = scheduling_manager.update_activity_instance(activity_instance1.activity_instance_id,
                                                                         start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Asia/Kolkata')).replace(hour=1).isoformat('T')))
        retrieved_instance1 = ActivityInstance.objects.get(activity_instance_id=activity_instance1.activity_instance_id)
        self.assertEqual(activity_instance1.start_time, retrieved_instance1.start_time)

        activity_instance1 = scheduling_manager.update_activity_instance(activity_instance1.activity_instance_id,
                                                                         end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Greenwich')).replace(hour=14).isoformat('T')))
        retrieved_instance1 = ActivityInstance.objects.get(activity_instance_id=activity_instance1.activity_instance_id)
        self.assertEqual(activity_instance1.end_time, retrieved_instance1.end_time)

        activity_instance1 = scheduling_manager.update_activity_instance(activity_instance1.activity_instance_id,
                                                                         price=15.23)

        retrieved_instance1 = ActivityInstance.objects.get(activity_instance_id=activity_instance1.activity_instance_id)
        self.assertEqual(activity_instance1.price, float(retrieved_instance1.price))

        activity_instance1 = scheduling_manager.update_activity_instance(activity_instance1.activity_instance_id,
                                                                         capacity=20)
        retrieved_instance1 = ActivityInstance.objects.get(activity_instance_id=activity_instance1.activity_instance_id)
        self.assertEqual(activity_instance1.capacity, retrieved_instance1.capacity)

        activity_instance1 = scheduling_manager.update_activity_instance(activity_instance1.activity_instance_id,
                                                                         bookings=10)
        retrieved_instance1 = ActivityInstance.objects.get(activity_instance_id=activity_instance1.activity_instance_id)
        self.assertEqual(activity_instance1.bookings, retrieved_instance1.bookings)

        activity_instance1 = scheduling_manager.update_activity_instance(activity_instance1.activity_instance_id,
                                                                         bookings=15,
                                                                         capacity=25,
                                                                         start_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Iran')).replace(hour=2, month=9).isoformat('T')),
                                                                         end_time=util.iso8601_to_utc_timestamp(datetime.now(tz=pytz.timezone('Turkey')).replace(hour=4, month=9).isoformat('T')),
                                                                         price=300)
        retrieved_instance1 = ActivityInstance.objects.get(activity_instance_id=activity_instance1.activity_instance_id)
        self.assertEqual(activity_instance1.bookings, retrieved_instance1.bookings)
        self.assertEqual(activity_instance1.capacity, retrieved_instance1.capacity)
        self.assertEqual(activity_instance1.start_time, retrieved_instance1.start_time)
        self.assertEqual(activity_instance1.end_time, retrieved_instance1.end_time)
        self.assertEqual(activity_instance1.price, float(retrieved_instance1.price))

        with self.assertRaises(BookingsCountInvalidException):
            activity_instance1 = scheduling_manager.update_activity_instance(activity_instance1.activity_instance_id,
                                                                             bookings=30)

        with self.assertRaises(BookingsCountInvalidException):
            activity_instance1 = scheduling_manager.update_activity_instance(activity_instance1.activity_instance_id,
                                                                             capacity=100,
                                                                             bookings=500)

        with self.assertRaises(BookingsCountInvalidException):
            activity_instance1 = scheduling_manager.update_activity_instance(activity_instance1.activity_instance_id,
                                                                             bookings=1100,
                                                                             capacity=200)

        try:
            activity_instance1 = scheduling_manager.update_activity_instance(activity_instance1.activity_instance_id,
                                                                             bookings=1,
                                                                             capacity=1)
        except BookingsCountInvalidException:
            self.fail("Equal capacity and bookings value raised exception.")


        with self.assertRaises(InvalidCapacityException):
            activity_instance1 = scheduling_manager.update_activity_instance(activity_instance1.activity_instance_id,
                                                                             capacity=0)

        with self.assertRaises(InvalidCapacityException):
            activity_instance1 = scheduling_manager.update_activity_instance(activity_instance1.activity_instance_id,
                                                                             capacity=0,
                                                                             bookings=12)

        with self.assertRaises(InvalidCapacityException):
            activity_instance1 = scheduling_manager.update_activity_instance(activity_instance1.activity_instance_id,

                                                                             capacity=-1)


def create_vendor(vendor_name):
    vendor = Vendor(name=vendor_name)
    vendor.save()
    return vendor


def delete_vendor(vendor):
    vendor.delete()


def create_activity(activity_name, vendor):
    activity = Activity(name=activity_name, vendor=vendor)
    activity.save()
    return activity


def delete_activity(activity):
    activity.delete()