#
# Copyright 2020 Red Hat, Inc.
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
"""Date-based Generators."""

from .base import BaseGenerator
from exceptions import NiseGeneratorError
from util import DateHelper, get_from_config, LOG


class ChronoGenerator(BaseGenerator):
    """A date-aware, chronological generator.

    This generator will generate dates such that:
        start_date <= generated_date <= end_date

    Each iteration of this generator will generate values in chronological
    order from start_date to end_date in 1-hour increments.
    """

    #
    # sub-classes should override these class variables.
    #

    # name of report period columns
    _period_start = "start_date"
    _period_end = "end_date"

    # name of usage interval columns
    _usage_start = "usage_start"
    _usage_end = "usage_end"

    def __init__(self, config):
        """Constructor."""
        # billing period dates (e.g. Jan 1 1900 - Jan 31 1900)
        self.start_date = get_from_config("name", self._period_start, config).get("default")
        self.end_date = get_from_config("name", self._period_end, config).get("default")

        self.period_start_format = get_from_config("name", self._period_start, config).get("format")
        self.period_end_format = get_from_config("name", self._period_end, config).get("format")

        # usage period dates (e.g. Jan 1 1900 12:00:00 - Jan 1 1900 13:00:00)
        self.last_usage_interval_start = None
        self.last_usage_interval_end = None

        self.usage_start_format = get_from_config("name", self._usage_start, config).get("format")
        self.usage_end_format = get_from_config("name", self._usage_end, config).get("format")

        self.datehelper = DateHelper()

        super().__init__(config)

    def _check_date(self, value):
        if self.start_date <= value and value <= self.end_date:
            return True
        raise NiseGeneratorError(f"Date value {value} is after end date {self.end_date}")

    def gen_datetime(self, **kwargs):
        """Generate datetime values."""
        colname = kwargs.get("name")

        if colname == self._period_start:
            self._check_date(self.start_date)
            return self.start_date.strftime(self.period_start_format)

        if colname == self._period_end:
            self._check_date(self.end_date)
            return self.end_date.strftime(self.period_end_format)

        if colname == self._usage_start:
            if self.last_usage_interval_start:
                nextval = self.last_usage_interval_start + self.datehelper.one_hour
                self._check_date(nextval)
                self.last_usage_interval_start = nextval
                return nextval.strftime(self.usage_start_format)
            else:
                self._check_date(self.start_date)
                self.last_usage_interval_start = self.start_date
                return self.last_usage_interval_start.strftime(self.usage_start_format)

        if colname == self._usage_end:
            if self.last_usage_interval_end:
                nextval = self.last_usage_interval_end + self.datehelper.one_hour
                self._check_date(nextval)
                self.last_usage_interval_end = nextval
                return nextval.strftime(self.usage_end_format)
            else:
                nextval = self.start_date + self.datehelper.one_hour
                self._check_date(nextval)
                self.last_usage_interval_end = nextval
                return nextval.strftime(self.usage_end_format)

        raise NiseGeneratorError(f"Unknown datetime column, '{colname}'. Unable to generate a value.")
