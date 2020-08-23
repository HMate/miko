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


def to_sql_where_constraint(data: dict, like_columns: list) -> str:
    """Creates a where constraint part of an sql eury from a dictionary.
     For example:
        {key1: 'val1', key2: 'val2' } becomes
        " WHERE key1 = 'val1' AND key2 = 'val2'"
    """
    if len(data) == 0:
        return ""
    where = " WHERE {}"
    filters = []
    for k, v in data.items():
        if k in like_columns:
            filters.append("{0}::text ILIKE %({0})s".format(k))
            data[k] = '%{}%'.format(v)
        else:
            filters.append("{0} = %({0})s".format(k))
    return where.format(" AND ".join(filters))
