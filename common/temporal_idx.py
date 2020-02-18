from datetime import timedelta, datetime
import numpy as np


class DailyTemporalIdx:
    def __init__(self, start_minutes, end_minutes, time_interval_in_minutes):
        self.start_minutes = start_minutes
        self.end_minutes = end_minutes
        self.time_interval = time_interval_in_minutes
        self.ts_num = int((end_minutes - start_minutes) // time_interval_in_minutes)

    def time_to_ts(self, cur_time):
        minutes = cur_time.hour * 60 + cur_time.minute
        idx = ((minutes - self.start_minutes) // self.time_interval)
        if idx < 0 or idx >= self.ts_num:
            raise IndexError("cur_time {} is not in time range".format(cur_time))
        return idx


class TemporalIdx:
    """
    end time is exclusive
    """
    def __init__(self, start_time, end_time, time_interval_in_minutes):
        self.start_time = start_time
        self.end_time = end_time
        self.time_interval = time_interval_in_minutes
        self.ts_num = int((end_time - start_time).total_seconds() // (time_interval_in_minutes * 60))
        self.nb_ts_per_day = 1440 // self.time_interval

    def ts_to_datetime(self, ts):
        return self.start_time + timedelta(minutes=self.time_interval * ts)

    def datetime_to_ts(self, cur_time):
        ts = int((cur_time - self.start_time).total_seconds() // (self.time_interval * 60))
        if ts < 0 or ts >= self.ts_num:
            raise IndexError("cur_time {} is not in time range".format(cur_time))
        return ts

    def safe_datetime_to_ts(self, time):
        try:
            ts = self.datetime_to_ts(time)
            return ts
        except IndexError:
            return np.nan

    def query_range(self, start_time, end_time):
        start_time_ts = self.datetime_to_ts(start_time)
        end_time_ts = self.datetime_to_ts(end_time)
        return start_time_ts, end_time_ts

    def query_weekend_idx(self):
        start_time = self.start_time
        start_day = datetime(start_time.year, start_time.month, start_time.day)
        weekday = start_day.weekday()
        target_idx = []
        # the start time is a weekend
        if weekday >= 5:
            monday = start_day + timedelta(7 - weekday)
            remaining_weekend_idx = [t for t in range(0, self.datetime_to_ts(monday))]
            target_idx.extend(remaining_weekend_idx)
            saturday = start_day + timedelta(days=13 - weekday)
        else:
            saturday = start_day + timedelta(days=5 - weekday)
        while saturday < self.end_time:
            ts = self.datetime_to_ts(saturday)
            target_idx.extend([t for t in range(ts, ts + self.nb_ts_per_day * 2) if t < self.ts_num])
            saturday += timedelta(days=7)
        return target_idx

    def query_workday_idx(self):
        start_time = self.start_time
        start_day = datetime(start_time.year, start_time.month, start_time.day)
        weekday = start_day.weekday()
        target_idx = []
        # the start time is a workday
        if weekday < 5:
            saturday = start_day + timedelta(days=5 - weekday)
            remaining_weekday_idx = [t for t in range(0, self.datetime_to_ts(saturday)) if t < self.ts_num]
            target_idx.extend(remaining_weekday_idx)
        monday = start_day + timedelta(days=7 - weekday)
        while monday < self.end_time:
            ts = self.datetime_to_ts(monday)
            target_idx.extend([t for t in range(ts, ts + self.nb_ts_per_day * 5) if t < self.ts_num])
            monday += timedelta(days=7)
        return target_idx

    def query_weekday_idx(self, day_of_week):
        start_time = self.start_time
        start_day = datetime(start_time.year, start_time.month, start_time.day)
        start_weekday = start_day.weekday()
        target_idx = []
        day = start_day + timedelta(day_of_week - start_weekday)
        while day < self.end_time:
            if day < self.start_time:
                day += timedelta(days=7)
                continue
            ts = self.datetime_to_ts(day)
            target_idx.extend([t for t in range(ts, ts + self.nb_ts_per_day) if t < self.ts_num])
            day += timedelta(days=7)
        return target_idx

    def query_day_idx(self):
        # day hours: [6,18)
        start_time = self.start_time
        start_day = datetime(start_time.year, start_time.month, start_time.day)
        start_ts_of_the_day = int((start_time - start_day).total_seconds()) // (60 * self.time_interval)
        start_hour = start_ts_of_the_day / (self.nb_ts_per_day / 24)
        target_idx = []
        if start_hour < 6:
            ts = self.datetime_to_ts(start_day + timedelta(hours=6))
            target_idx.extend([t for t in range(ts, ts + 12 * int((self.nb_ts_per_day / 24))) if t < self.ts_num])
        elif 6 <= start_hour < 18:
            first_night_time = start_day + timedelta(hours=18)
            remaining_day_idx = [t for t in range(0, self.datetime_to_ts(first_night_time)) if t < self.ts_num]
            target_idx.extend(remaining_day_idx)
        day_first_hour = start_day + timedelta(days=1) + timedelta(hours=6)
        while day_first_hour < self.end_time:
            ts = self.datetime_to_ts(day_first_hour)
            target_idx.extend([t for t in range(ts, ts + 12 * int((self.nb_ts_per_day / 24)))])
            day_first_hour += timedelta(hours=24)
        return target_idx

    def query_night_idx(self):
        # night hours: [18,24) [0,6)
        start_time = self.start_time
        start_day = datetime(start_time.year, start_time.month, start_time.day)
        start_ts_of_the_day = int((start_time - start_day).total_seconds()) // (60 * self.time_interval)
        start_hour = start_ts_of_the_day / (self.nb_ts_per_day / 24)
        target_idx = []
        if start_hour < 6:
            target_idx.extend([t for t in range(0, start_ts_of_the_day + 6 * int((self.nb_ts_per_day / 24))) if t < self.ts_num])
            target_idx.extend([t for t in range(start_ts_of_the_day + 18 * int((self.nb_ts_per_day / 24)),
                                                start_ts_of_the_day + 30 * int((self.nb_ts_per_day / 24))) if t < self.ts_num])
        elif start_hour < 18:
            target_idx.extend([t for t in range(start_ts_of_the_day + 18 * int((self.nb_ts_per_day / 24)),
                                                start_ts_of_the_day + 24 * int((self.nb_ts_per_day / 24))) if t < self.ts_num])
        else:
            target_idx.extend([t for t in range(0, start_ts_of_the_day + 30 * int((self.nb_ts_per_day / 24))) if t < self.ts_num])
        night_first_hour = start_day + timedelta(days=1) + timedelta(hours=18)
        while night_first_hour < self.end_time:
            ts = self.datetime_to_ts(night_first_hour)
            target_idx.extend([t for t in range(ts, ts + 13 * int((self.nb_ts_per_day / 24))) if t < self.ts_num])
            night_first_hour += timedelta(hours=24)
        return target_idx

    def query_hour_idx(self, hour_of_day):
        target_idx = []
        start_time = self.start_time
        start_day = datetime(start_time.year, start_time.month, start_time.day)
        start_ts_of_the_day = int((start_time - start_day).total_seconds()) // (60 * self.time_interval)
        start_hour = start_ts_of_the_day / (self.nb_ts_per_day / 24)
        if start_hour < hour_of_day:
            start_hour_ts = self.datetime_to_ts(start_day + timedelta(hours=hour_of_day))
            target_idx.extend([t for t in range(start_hour_ts, start_hour_ts + 1 * int((self.nb_ts_per_day / 24)))])
        elif start_hour == hour_of_day:
            start_hour_ts = self.datetime_to_ts(start_day + timedelta(hours=hour_of_day))
            target_idx.extend([t for t in range(start_hour_ts, start_hour_ts + 1 * int((self.nb_ts_per_day / 24)))])
        hour = start_day + timedelta(days=1) + timedelta(hours=hour_of_day)
        while hour < self.end_time:
            ts = self.datetime_to_ts(hour)
            target_idx.extend([t for t in range(ts, ts + 1 * int((self.nb_ts_per_day / 24)))])
            hour += timedelta(hours=24)
        return target_idx
