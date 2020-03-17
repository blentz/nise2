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
"""Cost and Usage Generator for OpenShift metering reports."""

from .date import ChronoGenerator

class OCPGenerator(ChronoGenerator):
    """Generator to generate lines compatible with OpenShift metering reports."""

    _period_start = 'report_period_start'
    _period_end = 'report_period_end'
    _usage_start = 'interval_start'
    _usage_end = 'interval_end'

    def gen_calc(self, **kwargs):
        return "NotImplemented: OCP:Calc"

    def gen_tag(self, **kwargs):
        return "NotImplemented: OCP:Tag"
