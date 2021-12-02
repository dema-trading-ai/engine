import datetime
import calendar

def dt2ts(dt):
    """Converts a datetime object to UTC timestamp

    naive datetime will be considered UTC.

    """

    return calendar.timegm(dt.utctimetuple())


x = datetime.datetime.strptime('2021-01-03 09:00:00', "%Y-%m-%d %H:%M:%S")
print(dt2ts(x))

# y = datetime.datetime.fromtimestamp(x, tz=datetime.timezone.utc)
# print(y)
#
# z = y.timestamp()
# print(z)
#