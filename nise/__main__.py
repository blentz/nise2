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
"""Cost and Usage Generator CLI."""
import argparse
import os
import sys
import yaml
from datetime import datetime

from faker import Faker
from util.date import DateHelper

from config import load_template, TEMPLATE_DIR
from util.log import LOG, LOG_VERBOSITY

FAKE = Faker()


def parse_args():
    """Create the parser for incoming data."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", action="count", default=0, help="increase verbosity (up to -vvv)")

    parser.add_argument(
        "--start",
        metavar="YYYY-MM-DD",
        dest="start_date",
        required=False,
        default=DateHelper.this_month_start,
        type=valid_date,
        help="Date to start generating data",
    )
    parser.add_argument(
        "--end",
        metavar="YYYY-MM-DD",
        dest="end_date",
        required=False,
        default=DateHelper.today,
        type=valid_date,
        help="Date to end generating data. Default is today.",
    )
    parser.add_argument(
        "--static-report-file", metavar="FILE", required=False, help="Generate static data based on yaml."
    )
    parser.add_argument(
        "--upload", metavar="ENDPOINT", required=False, help="URL for Red Hat Insights upload service."
    )

    # sub-commands
    subparsers = parser.add_subparsers(
        title="sub-commands", description="Supported sub-commands", help="data generator (required)", required=True
    )

    parser_aws = subparsers.add_parser("aws", help="generate aws data")
    aws_args(parser_aws)

    parser_azure = subparsers.add_parser("azure", help="generate azure data")
    azure_args(parser_azure)

    parser_gcp = subparsers.add_parser("gcp", help="generate gcp data")
    gcp_args(parser_gcp)

    parser_ocp = subparsers.add_parser("ocp", help="generate ocp data")
    ocp_args(parser_ocp)

    args = parser.parse_args()
    return args


def aws_args(parser):
    """AWS-specific CLI args"""
    parser.set_defaults(cmd="aws")
    parser.add_argument("--bucket", help="S3 bucket name.")
    parser.add_argument("--report-name", help="Cost report name.")
    parser.add_argument("--report-prefix", metavar="PREFIX", help="Cost report path prefix.")
    parser.add_argument(
        "--finalize",
        choices=["copy", "overwrite"],
        help="""Whether to generate finalized report data.
                            Can be either \'copy\' to produce a second finalized file locally
                            or \'overwrite\' to finalize the normal report files.
                            """,
    )


def azure_args(parser):
    """Azure-specific CLI args"""
    parser.set_defaults(cmd="azure")
    parser.add_argument("--container", help="Azure storage container name.")
    parser.add_argument("--report-name", help="Name of the cost report.")
    parser.add_argument("--report-prefix", help="Report directory prefix.")
    parser.add_argument(
        "--storage-account", default=os.getenv("AZURE_STORAGE_ACCOUNT"), help="Azure container to place the data.",
    )


def gcp_args(parser):
    """GCP-specific CLI args"""
    parser.set_defaults(cmd="gcp")
    parser.add_argument("--report-prefix", help="GCP Billing Report Prefix.")
    parser.add_argument("--bucket", help="GCP storage account to place the data.")


def ocp_args(parser):
    """OCP-specific CLI args"""
    parser.set_defaults(cmd="ocp")
    parser.add_argument("--clusterid", default=FAKE.word(), help="Cluster identifier for usage data.")


def valid_date(date_string):
    """Create date from date string."""
    try:
        valid = datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        msg = "{} is an unsupported date format.".format(date_string)
        raise argparse.ArgumentTypeError(msg)
    return valid


def main():
    """Run data generation program."""
    args = parse_args()
    if args.verbosity:
        LOG.setLevel(LOG_VERBOSITY[args.verbosity])
    LOG.debug("CLI Args: %s", args)

    tmpl_path = f"{TEMPLATE_DIR}/{args.cmd}"
    for fname in os.listdir(tmpl_path):
        if os.path.splitext(fname)[1] != ".yaml":
            continue

        tmpl_args = {
            "report_month": 1,
            "report_year": 1,
            "clusterid": args.clusterid,
        }

        LOG.debug(f"Loading: {tmpl_path}/{fname}")
        template = load_template(f"{args.cmd}/{fname}", **tmpl_args)
        ymldict = yaml.safe_load(template)
        LOG.debug(f"Rendered YAML: {ymldict}")

        generator = None
        header = None

        if args.cmd == 'ocp':
            from generators import OCPGenerator
            generator = OCPGenerator(ymldict)
            header = generator.header

        count = 0
        for line in generator.lines():
            if count >= 10:
                break
            count += 1


if __name__ == "__main__":
    main()
