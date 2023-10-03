import time
import tracemalloc

import calendar
from datetime import datetime


def time_memory_tracker(method):

    ### Log Level
    # 0: Nothing
    # 1: Print time and memory usage of function
    LOG_LEVEL = 1

    def method_with_trackers(*args, **kw):
        ts = time.time()
        tracemalloc.start()
        result = method(*args, **kw)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        te = time.time()
        duration = te - ts
        if LOG_LEVEL > 0:
            output = f"{method.__qualname__} executed in {round(duration, 2)} seconds, using up to {round(peak / 1024**2,2)}MB of RAM"
            print(output)
        return result
    return method_with_trackers



def get_last_day_of_month(date_str):
    """
    Parse a date string in '%Y-%m' format and return the last day of the month as a datetime object.
    Args:
        date_str (str): Date string in '%Y-%m' format (e.g., '2013-07').
    Returns:
        datetime: Last day of the month as a datetime object.
    """
    year, month = map(int, date_str.split('-'))
    last_day = calendar.monthrange(year, month)[1]
    last_day_date = datetime(year, month, last_day)
    return last_day_date
