import ast
import json
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.generic import View
from Scheduler.activity_instance_manager import ActivityInstanceManager
from SchedulerAPI import util


class ActivityInstanceView(View):
    def __init__(self):
        self.activity_instance_manager = ActivityInstanceManager()

    def get(self, request, activity_instance_id):
        activity_instance = self.activity_instance_manager.retrieve_activity_instance(activity_instance_id)
        if activity_instance is None:
            raise Http404
        else:
            activity_instance = convert_activity_instance_timestamp_to_iso(activity_instance)
            return HttpResponse(util.obj_to_json(activity_instance), content_type='application/json')

    def put(self, request, activity_instance_id):
        attributes_dictionary = ast.literal_eval(request.read().decode('utf-8'))

        if attributes_dictionary.get('start_time') is not None:
            attributes_dictionary['start_time'] = util.iso8601_to_utc_timestamp(attributes_dictionary['start_time'])
        if attributes_dictionary.get('end_time') is not None:
            attributes_dictionary['end_time'] = util.iso8601_to_utc_timestamp(attributes_dictionary['end_time'])

        activity_instance = self.activity_instance_manager.update_activity_instance(activity_instance_id,
                                                                                    **attributes_dictionary)
        if activity_instance is None:
            raise Http404
        else:
            activity_instance = convert_activity_instance_timestamp_to_iso(activity_instance)
            return HttpResponse(util.obj_to_json(activity_instance), content_type='application/json')

    def post(self, request, activity_instance_id=None):
        activity_id = request.POST.get('activity_id')
        start_time = util.iso8601_to_utc_timestamp(request.POST.get('start_time'))
        end_time = util.iso8601_to_utc_timestamp(request.POST.get('end_time'))
        price = float(request.POST.get('price'))
        capacity = int(request.POST.get('capacity'))
        bookings = request.POST.get('bookings')
        if bookings is None:
            activity_instance = self.activity_instance_manager.create_activity_instance(activity_id=activity_id,
                                                                                        start_time=start_time,
                                                                                        end_time=end_time,
                                                                                        price=price,
                                                                                        capacity=capacity)
        else:
            activity_instance = self.activity_instance_manager.create_activity_instance(activity_id=activity_id,
                                                                                        start_time=start_time,
                                                                                        end_time=end_time,
                                                                                        price=price,
                                                                                        capacity=capacity,
                                                                                        bookings=int(bookings))
        activity_instance = convert_activity_instance_timestamp_to_iso(activity_instance)
        return HttpResponse(util.obj_to_json(activity_instance), content_type='application/json')


    def delete(self, request, activity_instance_id):
        if self.activity_instance_manager.delete_activity_instance(activity_instance_id):
            return HttpResponse()
        else:
            raise Http404


def convert_activity_instance_timestamp_to_iso(activity_instance):
    activity_instance.start_time = util.timestamp_to_iso8601(activity_instance.start_time)
    activity_instance.end_time = util.timestamp_to_iso8601(activity_instance.end_time)
    return activity_instance
