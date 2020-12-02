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

import datetime
import pathlib
import os
import shutil

from dacot import version

now = datetime.datetime.now().strftime(f"%Y%m%d-{version.__version__}")


class Paths():
    def __init__(self):
        self._base = pathlib.Path("data")
        self._experiment = ""

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, val):
        self._base = pathlib.Path(val)

    @property
    def experiment(self):
        return self._experiment

    @experiment.setter
    def experiment(self, val):
        self._experiment = f"_{val}"

    @property
    def rawdata(self):
        return self.base / "raw" / f"raw{self.experiment}_{now}"

    @property
    def outdir(self):
        return self.base / "output" / f"output{self.experiment}_{now}"

    @property
    def interim(self):
        return self. base / "interim"

    def __str__(self):
        return f"""
                 Base path: {self.base}
    INE data download path: {self.rawdata}
         Interim data path: {self.interim}
     Output directory path: {self.outdir}
    """

PATHS = Paths()


def check_dirs(regenerate=False):
    print("Checking directories...")
    print(PATHS)
    PATHS.base.exists() or os.makedirs(PATHS.base)
    PATHS.interim.exists() or os.makedirs(PATHS.interim)
    PATHS.rawdata.exists() or os.makedirs(PATHS.rawdata)

    if PATHS.outdir.exists() and not regenerate:
        print(f"\t'{PATHS.outdir}' exists, not overwriting it")
        return False
    elif PATHS.outdir.exists() and regenerate:
        print(f"\t'{PATHS.outdir}' exists, deleting it")
        shutil.rmtree(PATHS.outdir, ignore_errors=True)
    return True
