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
import pathlib
import re
import tempfile
import urllib.parse
import zipfile

import requests

from dacot import utils

PATHS = utils.PATHS
URLS_COVID = ["https://www.ine.es/covid/datos_disponibles.zip"]
URLS_INE = [
    "https://www.ine.es/experimental/movilidad/"
    "movilidad_cotidiana_junio_octubre.zip",

    "https://www.ine.es/experimental/movilidad/"
    "movilidad_cotidiana_noviembre.zip",
]


def _download(urls, force=False):
    print("Downloading data...")

    for url in urls:
        aux = urllib.parse.urlparse(url)
        f = os.path.basename(aux.path)

        if (PATHS.rawdata / f).exists() and not force:
            print(f"\t {url} already downloaded, not overwriting it "
                  "(force=False)")
            return

        print(f"\t downloading {url}")
        f = PATHS.rawdata / f
        resp = requests.get(url)
        with open(f, 'wb') as f:
            f.write(resp.content)


def _prepare_covid():
    print("Preparing data...")

    with tempfile.TemporaryDirectory(dir=PATHS.base) as tmpdir:
        tmpdir = pathlib.Path(tmpdir)
        for zf in PATHS.rawdata.glob('**/*.zip'):
            # Extract zip container
            with zipfile.ZipFile(zf, 'r') as zf:
                zf.extractall(tmpdir)

        # Extract individual zip files
        for f in tmpdir.glob('**/*.zip'):
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

        outdir = tmpdir / PATHS.outdir.name
        outdir.mkdir()

        r = re.compile(r".*_([0-9]{2}[A-Z]{3}).*\.csv$")

        # if we use the generator we will get also the new files being created
        # therefore the loop will fail.
        csvfiles = list(tmpdir.glob("**/*csv"))
        for f in csvfiles:
            aux = r.search(f.as_posix())
            if not aux:
                continue

            day = aux.group(1)[:2]
            month = aux.group(1)[2:]
            month = datemap.get(month)

            date = f"2020-{month}-{day}"
            aux = outdir / date / "original" / f.name
            aux.parent.mkdir(parents=True, exist_ok=True)
            f.rename(aux)

        # Now move November data
        date = "2019-11"
        aux = outdir / date / "original"
        aux.mkdir(parents=True, exist_ok=True)

        files = [
            "Flujos+15_O-D_M1_NOV.csv",
            "PobxCeldasDestinoM1_NOV.csv",
            "PobxCeldasOrigenM1_NOV.csv",
        ]
        for f in files:
            f = tmpdir / "Noviembre 2019" / f
            f.parent.mkdir(parents=True, exist_ok=True)
            f.rename(aux / f.name)

        outdir.rename(PATHS.outdir)


def _prepare_ine():
    print("Preparing data...")

    with tempfile.TemporaryDirectory(dir=PATHS.base) as tmpdir:
        tmpdir = pathlib.Path(tmpdir)

        for zf in PATHS.rawdata.glob('**/*.zip'):
            # Extract zip container
            with zipfile.ZipFile(zf, 'r') as zf:
                zf.extractall(tmpdir)

        # Extract individual zip files
        for f in os.listdir(tmpdir):
            if not f.endswith(".zip"):
                continue

            f = os.path.join(tmpdir, f)
            with zipfile.ZipFile(f) as zf:
                zf.extractall(tmpdir)

        # Now prepare output

        outdir = tmpdir / PATHS.outdir.name
        outdir.mkdir()

        r = re.compile(r".*_([0-9]{2}[0-9]{2})\.xlsx$")

        # if we use the generator we will get also the new files being created
        # therefore the loop will fail.
        lsfiles = list(tmpdir.glob('**/Tabla*.xlsx'))
        for f in lsfiles:
            aux = r.search(f.as_posix())
            if not aux:
                continue

            day = aux.group(1)[:2]
            month = aux.group(1)[2:]

            date = f"2020-{month}-{day}"
            aux = outdir / date / "original" / f.name
            aux.parent.mkdir(parents=True, exist_ok=True)
            f.rename(aux)

        outdir.rename(PATHS.outdir)
        print(f"\t data saved into {PATHS.outdir}")


def do_covid_mobility(force=False):
    _download(URLS_COVID, force=force)
    _prepare_covid()


def do_ine_mobility(force=False):
    _download(URLS_INE, force=force)
    _prepare_ine()
