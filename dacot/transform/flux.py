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

import pandas

from dacot import utils

PATHS = utils.PATHS


def convert(filename, cell, ine_cells):
    df = pandas.read_csv(
        filename,
        sep=";",
        encoding="ISO-8859-1"
    )
    df.columns = [c.lower().strip() for c in df.columns]

    cell = cell.lower()
    df["province"] = df[cell].apply(lambda x: ine_cells.get(x.strip())[1])
    df["pid"] = df[cell].apply(lambda x: ine_cells.get(x.strip())[0])

    cols = ["province", "pid"]
    for c in df.columns:
        if c.startswith("unnamed") or c in cols:
            continue
        cols.append(c)

    df = df[cols]

    return df


def convert_flux(filename, ocell, dcell, ine_cells):
    df = pandas.read_csv(
        filename,
        sep=";",
        encoding="ISO-8859-1"
    )
    df.columns = [c.lower().strip() for c in df.columns]

    ocell = ocell.lower()
    dcell = dcell.lower()
    df["prv orig"] = df[ocell].apply(lambda x: ine_cells.get(x.strip())[1])
    df["pid orig"] = df[ocell].apply(lambda x: ine_cells.get(x.strip())[0])
    df["prv dest"] = df[dcell].apply(lambda x: ine_cells.get(x.strip())[1])
    df["pid dest"] = df[dcell].apply(lambda x: ine_cells.get(x.strip())[0])

    agg = {"pid orig": max, "pid dest": max, "flujo": sum}
    grouped = df.groupby(["prv orig", "prv dest"]).aggregate(agg).reset_index()
    df_intra = grouped.loc[grouped["prv orig"] == grouped["prv dest"]]
    df_intra = df_intra[["prv orig", "pid orig", "flujo"]]
    df_intra.columns = ["province", "pid", "flux"]
    df_intra = df_intra.reset_index(drop=True)
#    print("-")
#    print(df_intra.head())
#    print("-")
    df_inter = grouped.loc[grouped["prv orig"] != grouped["prv dest"]]
    df_inter.columns = ["prv orig", "prv dest", "pid orig", "pid dest", "flux"]
    df_inter = df_inter.reset_index(drop=True)
#    print("-")
#    print(df_inter.head())
#    print("-")

    cols = ["prv orig", "pid orig", "prv dest", "pid dest"]
    for c in df.columns:
        if c.startswith("unnamed") or c in cols:
            continue
        cols.append(c)
    df = df[cols]
#    print(df.head())

    return df, df_intra, df_inter


def do():
    print("Transforming cell data into provinces...")
    ine_cells = pandas.read_csv(PATHS.interim / "celdas.csv")

    ine_cells = dict([
        (i, (j, k))
        for i, j, k in ine_cells.groupby(
            ["ID_GRUPO", "CPRO", "NPRO"]
        ).groups.keys()
    ])

    agg_flux = []
    agg_flux_intra = []
    agg_flux_inter = []
    for d, _, files in os.walk(PATHS.outdir):
        if not d.endswith("original"):
            continue
        d = pathlib.Path(d)

        print(f"Processing {d}...")

        for f in files:
            aux = d / f
            if f.startswith("PobxCeldasDestino"):
                cell = "CELDA_DESTINO"
                df = convert(aux, cell, ine_cells)
                df.to_csv(os.path.join(d, "pop_dest.csv"), index=False)

            elif f.startswith("PobxCeldasOrigen"):
                cell = "CELDA_ORIGEN"
                df = convert(aux, cell, ine_cells)
                df.to_csv(os.path.join(d, "pop_orig.csv"), index=False)

            elif f.startswith("FlujosDestino100"):
                ocell = "CELDA_ORIGEN"
                dcell = "CELDA_DESTINO"
                df, df_intra, df_inter = convert_flux(aux,
                                                      ocell,
                                                      dcell,
                                                      ine_cells)

                date = pandas.to_datetime(d.parent.name)

                df.insert(0, "date", date)
                agg_flux.append(df)

                df_intra.insert(0, "date", date)
                agg_flux_intra.append(df_intra)

                df_inter.insert(0, "date", date)
                agg_flux_inter.append(df_inter)

                aux = d.parent / "province_flux"
                print(f"\t saving into {aux}")
                os.mkdir(aux)
                df.to_csv(aux / "flux.csv", index=False)
                df_inter.to_csv(aux / "flux_inter.csv", index=False)
                df_intra.to_csv(aux / "flux_intra.csv", index=False)

    df = pandas.concat(agg_flux)
    df = df.sort_values(["date", "prv orig"]).reset_index(drop=True)
    df.to_csv(PATHS.outdir / "province_flux.csv", index=False)

    df = pandas.concat(agg_flux_intra)
    df = df.sort_values(["date", "province"]).reset_index(drop=True)
    df.to_csv(PATHS.outdir / "province_flux_intra.csv", index=False)

    df = pandas.concat(agg_flux_inter)
    df = df.sort_values(["date", "prv orig"]).reset_index(drop=True)
    df.to_csv(PATHS.outdir / "province_flux_inter.csv", index=False)
