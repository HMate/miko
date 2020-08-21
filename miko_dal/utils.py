import datetime
import json


class MikoJsonEncoder(json.JSONEncoder):
    def default(self, o):
        """We also want to support datetime.timedelta, which flask doesnt"""
        if isinstance(o, datetime.timedelta):
            return str(o)
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        if isinstance(o, datetime.date):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)