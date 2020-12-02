# Copyright (c) 2020 Spanish National Research Council
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import sys

from dacot import data
from dacot.transform import flux
from dacot import utils
from dacot import version

parser = argparse.ArgumentParser(
    prog="dacot",
    description='Download and process DataCOVID INE data.'
)

parser.add_argument(
    "--force",
    action="store_true",
    default=False,
    help="Force download of data, even if files exist"
)

parser.add_argument(
    "--regenerate",
    action="store_true",
    default=False,
    help="Force overwriting of output directory"
)

parser.add_argument(
    "--base",
    metavar="DIRECTORY",
    action="store",
    default="data",
    help="Base directory to use (defaults to ./data)"
)

parser.add_argument(
    "experiment",
    type=str,
    choices=("em3", "em2", "covid"),
    default=None,
    help="""Download INE mobility data or INE COVID mobility data, choices are:

    em3: Download data from the INE Mobility study, available at
              https://www.ine.es/experimental/movilidad/experimental_em3.htm
    em2, covid: Download data from the DataCOVID INE study, available at
              https://www.ine.es/covid/covid_movilidad.htm
    """,
)


def main():
    print(f"dacot version {version.__version__}")
    args = parser.parse_args(sys.argv[1:])

    force = args.force
    regenerate = args.regenerate
    if args.base:
        utils.PATHS.base = args.base

    if args.experiment in ("mobility", "em3"):
        print("Using EM3 data (24/06/2020 to 30/12/2020)")
        print("Check https://www.ine.es/experimental/movilidad/"
              "experimental_em3.htm for more details")
        utils.PATHS.experiment = "em3"
    else:
        print("Using EM2 (COVID) data (16/03/2020 to 20/06/2020)")
        print("Check https://www.ine.es/covid/covid_movilidad.htm "
              "for more details")
        utils.PATHS.experiment = "em2"

    if not utils.check_dirs(regenerate=regenerate):
        sys.exit(1)

    if args.experiment in ("mobility", "em3"):
        print("-" * 80)
        data.do_ine_mobility(force=force)
        print("-" * 80)
        flux.do_mobility()
        print("-" * 80)
    else:
        print("-" * 80)
        data.do_covid_mobility(force=force)
        print("-" * 80)
        flux.do_covid()
        print("-" * 80)


if __name__ == "__main__":
    main()
