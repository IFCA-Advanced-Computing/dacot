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

now = datetime.datetime.now().strftime("%Y%m%d%H%M%S%s")


class Paths():
    base = pathlib.Path("data")
    inedata = base / "raw" / f"datos_disponibles_{now}.zip"
    inedata = base / "raw" / f"datos_disponibles.zip"
    outdir = base / "output" / f"output_{now}"
    interim = base / "interim"


PATHS = Paths()
