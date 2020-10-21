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


def main():
    print(f"dacot version {version.__version__}")
    args = parser.parse_args(sys.argv[1:])

    force = args.force
    regenerate = args.regenerate
    if args.base:
        utils.PATHS.base = args.base

    if not utils.check_dirs(regenerate=regenerate):
        sys.exit(1)

    print("-" * 80)
    data.do(force=force)
    print("-" * 80)
    flux.do()
    print("-" * 80)


if __name__ == "__main__":
    main()
