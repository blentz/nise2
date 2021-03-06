#
# Copyright 2018 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Date utilities."""

from datetime import datetime, timedelta

import pytz


class DateHelper:
    """Helper class with convenience functions."""

    def __init__(self, utc=False):
        """Initialize when now is."""
        self.now = datetime.now(tz=pytz.UTC)

    @property
    def one_day(self):
        """Timedelta of one day."""
        return timedelta(days=1)

    @property
    def one_hour(self):
        """Timedelta of one hour."""
        return timedelta(minutes=60)

    @property
    def this_hour(self):
        """Datetime of top of the current hour."""
        return self.now.replace(microsecond=0, second=0, minute=0)

    @property
    def next_hour(self):
        """Datetime of top of the next hour."""
        next_hour = (self.this_hour + self.one_hour).hour
        return self.this_hour.replace(hour=next_hour)

    @property
    def previous_hour(self):
        """Datetime of top of the previous hour."""
        prev_hour = (self.this_hour - self.one_hour).hour
        return self.this_hour.replace(hour=prev_hour)

    @property
    def today(self):
        """Datetime of midnight today."""
        return self.now.replace(microsecond=0, second=0, minute=0, hour=0)

    @property
    def yesterday(self):
        """Datetime of midnight yesterday."""
        return self.today - self.one_day

    @property
    def tomorrow(self):
        """Datetime of midnight tomorrow."""
        return self.today + self.one_day

    @property
    def this_month_start(self):
        """Datetime of midnight on the 1st of this month."""
        return self.this_hour.replace(microsecond=0, second=0, minute=0, hour=0, day=1)

    @property
    def last_month_start(self):
        """Datetime of midnight on the 1st of the previous month."""
        last_month = self.this_month_start - self.one_day
        return last_month.replace(day=1)

    @property
    def next_month_start(self):
        """Datetime of midnight on the 1st of next month."""
        return self.this_month_end + self.one_day

    @property
    def this_month_end(self):
        """Datetime of midnight on the last day of this month."""
        month_end = self.days_in_month(self.this_month_start)
        return self.this_month_start.replace(day=month_end)

    @property
    def last_month_end(self):
        """Datetime of midnight on the last day of the previous month."""
        month_end = self.days_in_month(self.last_month_start)
        return self.last_month_start.replace(day=month_end)

    @property
    def next_month_end(self):
        """Datetime of midnight on the last day of next month."""
        month_end = self.days_in_month(self.next_month_start)
        return self.next_month_start.replace(day=month_end)

    def month_start(self, in_date):
        """Datetime of midnight on the 1st of in_date month."""
        return in_date.replace(microsecond=0, second=0, minute=0, hour=0, day=1)

    def month_end(self, in_date):
        """Datetime of midnight on the last day of the in_date month."""
        month_end = self.days_in_month(in_date)
        return in_date.replace(microsecond=0, second=0, minute=0, hour=0, day=month_end)

    def next_month(self, in_date):
        """Return the first of the next month from the in_date.

        Args:
            in_date    (DateTime) input datetime
        Returns:
            (DateTime): First of the next month

        """
        num_days = self.days_in_month(in_date)
        dt_next_month = in_date.replace(day=num_days, hour=0, minute=0, second=0, microsecond=0) + self.one_day
        return dt_next_month

    def previous_month(self, in_date):
        """Return the first of the previous month from the in_date.

        Args:
            in_date    (DateTime) input datetime
        Returns:
            (DateTime): First of the previous month

        """
        dt_prev_month = in_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - self.one_day
        return dt_prev_month.replace(day=1)

    def n_days_ago(self, in_date, n_days):
        """Return midnight of the n days from the in_date in past.

        Args:
            in_date    (DateTime) input datetime
            n_days     (integer) number of days in the past
        Returns:
            (DateTime): A day n days in the past

        """
        midnight = in_date.replace(hour=0, minute=0, second=0, microsecond=0)
        n_days = midnight - timedelta(days=n_days)
        return n_days

    def list_days(self, start_date, end_date):
        """Return a list of days from the start date til the end date.

        Args:
            start_date    (DateTime) starting datetime
            end_date      (DateTime) ending datetime
        Returns:
            (List[DateTime]): A list of days from the start date to end date

        """
        end_midnight = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        start_midnight = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        days = (end_midnight - start_midnight + self.one_day).days
        return [start_midnight + timedelta(i) for i in range(days)]

    def list_months(self, start_date, end_date):
        """Return a list of months from the start date til the end date.

        Args:
            start_date    (DateTime) starting datetime
            end_date      (DateTime) ending datetime
        Returns:
            (List[DateTime]): A list of months from the start date to end date

        """
        months = []
        dt_first = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_midnight = end_date.replace(hour=23, minute=59, second=59, microsecond=0)

        current = dt_first
        while current < end_midnight:
            months.append(current)
            num_days = self.days_in_month(current)
            next_month = current.replace(day=num_days) + self.one_day
            current = next_month
        return months

    def days_in_month(self, date):
        """Return the number of days in the month.

        Args:
            date (datetime.datetime)

        Returns:
            (int) number of days in the month

        """
        # monthrange returns (day_of_week, num_days)
        _, num_days = calendar.monthrange(date.year, date.month)
        return num_days
