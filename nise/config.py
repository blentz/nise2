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
"""Nise configuration loader/parser."""

import os

from jinja2 import Environment, FileSystemLoader, Template
from util.log import LOG

from util.jinja_helpers import faker_passthrough

TEMPLATE_DIR = os.path.dirname(os.path.realpath(__file__)) + "/templates"


def load_template(template, **kwargs):
    """ Load and render a Jinja template

    Args:
        template (str) relative path to a template in TEMPLATE_DIR
        kwargs (dict) keyword args required to render the template

    Returns:
        (str) rendered template
    """

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    env.globals["faker"] = faker_passthrough
    tmpl = env.get_template(template)

    rendered = tmpl.render(**kwargs)
    LOG.debug(f"Rendered template '{template}': {rendered}")
    return rendered
