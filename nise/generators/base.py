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
"""Base Generator."""

import csv
import re
from datetime import datetime

from faker import Faker

from util.log import LOG
from exceptions import NiseError, NiseGeneratorError


def count_brackets(somestr):
    """Count the number of instances of {} """
    return len(re.findall("{.*?}", somestr))


class BaseGenerator:
    """Generator object to generate lines in a CSV file.

        Sub-classes should implement methods for generating supported column
        types. Each gen_*() method should return one value so that each
        iteration of lines() can return one complete row of data.

        Example generation method:

            def gen_SOMETYPE(self, **kwargs):
                '''generate value for SOMETYPE column.'''
                generated_column_value = your_code_here()

                if bad_thing_happens:
                    raise NiseGeneratorError("Something unexpected happened!")

                return generated_column_value
    """

    FAKE = Faker()

    def __init__(self, config):
        """Constructor.

        Args:
            config (dict) compiled configuration

        Config Definition:
            { "filename": "name of the file to be generated"
              "columns": [
                { "name": "column name",
                 "type": "column type",
                 "default": "default column value",
                 "format": "format for generating new column values"
                 "seed": ["seeded", "values", "used", "during", "generation"]
                },
                {...},
                {...},
              ]
            }

        Supported column types:
            - string:
                a string. the format field is passed to str.format()
            - datetime:
                a datetime object. the format field is passed to datetime.strptime()
            - tag:
                a list of key-value pairs.  the format field is implementation-specific
            - calc:
                a calculated value. the calculation is implementation-specific

        """
        self.config = config
        filename = self.config.get("filename")
        LOG.info(f"Generator initialized for file: {filename}")


    @property
    def header(self):
        """return a CSV header"""
        header = [col["name"] for col in self.config.get("columns")]
        LOG.debug(f"Header: {header}")
        return header

    def lines(self):
        """Generator function to emit randomized CSV lines

        send() can be used to propagate a new column definition into the generator that is used on
        the next iteration.

        throw() will raise the given exception, except NiseGeneratorError and AttributeError
        """
        output = []
        sent = None
        while True:
            output = []
            columns = sent if sent else self.config.get("columns")
            for col in columns:
                self.validate(col)
                # if type=FOO, call self.gen_FOO(**col)
                result = col.get("default")
                try:
                    coltype = col.get("type")
                    result = getattr(self, f"gen_{coltype}")(**col)
                except NiseGeneratorError as exc:
                    LOG.info(exc)
                except AttributeError as exc:
                    LOG.info(f"No method to generate columns of type '{coltype}'. Using default value.")
                output.append(result)
            LOG.debug(f"Generated Line: {output}")
            sent = yield output

    def validate(self, column):
        """Validate column configuration."""
        colname = column.get("name")
        if not colname:
            raise NiseError(f"Column name missing: {column}")

        coltype = column.get("type")
        if not coltype:
            raise NiseError(f"Column type missing for column '{colname}'")

    def _return_default(self, **kwargs):
        """Convenience method for returning the default value."""
        default = kwargs.get("default")
        if default:
            return default
        name = kwargs.get("name")
        raise NiseGeneratorError("No default value defined for column '{name}'.")

    def gen_string(self, **kwargs):
        """Generate string values."""
        colformat = kwargs.get("format")
        if colformat:
            generated = [self.FAKE.word() for _ in range(0, count_brackets(colformat))]
            return kwargs.get("format").format(*generated)
        return self._return_default(**kwargs)

    def gen_datetime(self, **kwargs):
        """Generate datetime values.

        NOTE: This method makes no effort to do any kind of validation.
              For example, it does not ensure "end" dates are after "before" dates.

        Sub-classes should override this method.
        """
        colformat = kwargs.get("format")
        if colformat:
            return self.FAKE.date(pattern=colformat)
        return self._return_default(**kwargs)

    def gen_calc(self, **kwargs):
        """Generate calculated values.

        Sub-classes should override this method.
        """
        return self.FAKE.random_digit()
