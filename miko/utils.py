import datetime
import flask


class MikoJsonEncoder(flask.json.JSONEncoder):
    def default(self, o):
        """We also want to support datetime.timedelta, which flask doesnt"""
        if isinstance(o, datetime.timedelta):
            return str(o)
        return flask.json.JSONEncoder.default(self, o)