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

import os
import os.path
import re
import shutil
import tempfile
import zipfile

import requests

from dacot import utils

PATHS = utils.PATHS
URL = "https://www.ine.es/covid/datos_disponibles.zip"


def _download(force=False):
    print("Downloading data...")
    resp = requests.get(URL)
    with open(PATHS.inedata, 'wb') as f:
        f.write(resp.content)


def _prepare():
    print("Preparing data...")

    with tempfile.TemporaryDirectory(dir=PATHS.base) as tmpdir:
        # Extract zip container
        with zipfile.ZipFile(PATHS.inedata, 'r') as zf:
            zf.extractall(tmpdir)

        # Extract individual zip files
        for f in os.listdir(tmpdir):
            if not f.endswith(".zip"):
                continue

            f = os.path.join(tmpdir, f)
            with zipfile.ZipFile(f) as zf:
                zf.extractall(tmpdir)

        # Rename csv files to something that makes sense
        datemap = {
            "MAR": "03",
            "ABR": "04",
            "MAY": "05",
            "JUN": "06",
            "JUL": "07",
            "AGO": "08",
            "SEP": "09",
        }

        # Now prepare output

        outdir = os.path.join(tmpdir, PATHS.outdir.name)
        os.mkdir(outdir)

        r = re.compile(r".*_([0-9]{2}[A-Z]{3}).*\.csv$")
        for f in os.listdir(tmpdir):
            aux = r.search(f)
            if not aux:
                continue

            f = os.path.join(tmpdir, f)

            day = aux.group(1)[:2]
            month = aux.group(1)[2:]
            month = datemap.get(month)

            date = f"2020-{month}-{day}"
            aux = os.path.join(outdir, date, "original")
            if not os.path.exists(aux):
                os.makedirs(aux)
            shutil.move(f, aux)

        # Now move November data
        date = "2020-11"
        aux = os.path.join(outdir, date, "original")
        if not os.path.exists(aux):
            os.makedirs(aux)
        files = [
            "FlujosDestino100+_M1_NOV.csv",
            "FlujosOrigen100+_M1_NOV.csv",
            "PobxCeldasDestinoM1_NOV.csv",
            "PobxCeldasOrigenM1_NOV.csv"
        ]
        for f in files:
            f = os.path.join(tmpdir, f)
            shutil.move(f, aux)

        shutil.move(outdir, PATHS.outdir)
        print(f"\t data saved into {PATHS.outdir}")


def do():
#    _download()
    _prepare()
