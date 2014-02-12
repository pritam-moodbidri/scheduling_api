import calendar
from datetime import datetime
import json
import dateutil.parser


def iso8601_to_utc_timestamp(date):
    date_datetime = dateutil.parser.parse(date)
    utc_timestamp = calendar.timegm(date_datetime.utctimetuple())
    return utc_timestamp


def timestamp_to_iso8601(timestamp):
    date = datetime.fromtimestamp(timestamp)
    return date.isoformat('T')


def obj_to_json(obj):
    json_dictionary = {}

    for (key, value) in obj.__dict__.items():
        if key[:1] != '_':
            json_dictionary[key] = str(value)

    return json.dumps(json_dictionary)