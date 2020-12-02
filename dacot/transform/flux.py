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


def map_ine_cells_to_provinces(df, ocell, dcell=None):
    cells = pandas.read_csv(PATHS.interim / "celdas.csv")

    cells = dict([
        (i, (j, k))
        for i, j, k in cells.groupby(
            ["ID_GRUPO", "CPRO", "NPRO"]
        ).groups.keys()
    ])

    if ocell and dcell:
        df["province origin"] = df[ocell].apply(
            lambda x: cells.get(x.strip())[1]
        )
        df["province id origin"] = df[ocell].apply(
            lambda x: cells.get(x.strip())[0]
        )
        df["province destination"] = df[dcell].apply(
            lambda x: cells.get(x.strip())[1]
        )
        df["province id destination"] = df[dcell].apply(
            lambda x: cells.get(x.strip())[0]
        )
    else:
        df["province"] = df[ocell].apply(lambda x: cells.get(x.strip())[1])
        df["province id"] = df[ocell].apply(lambda x: cells.get(x.strip())[0])


def add_province_and_region_data(df, search_by_id=True):
    prov = pandas.read_csv(
        PATHS.interim / "provincias-ine.csv",
        sep=";"
    )

    for what in ("origin", "destination"):
        if search_by_id:
            df_col = f"province id {what}"
            prov_col = "id provincia"
        else:
            df_col = f"province {what}"
            prov_col = "provincia"

        replace_cols = (
            f"province {what}",
            f"province id {what}",
            f"region {what}",
            f"region id {what}"
        )

        replace_with = [
            "provincia",
            "id provincia",
            "autonomia",
            "id auto"
        ]

        for p in df[df_col].unique():
            if p not in prov[prov_col].values:
#                print("--", p)
                continue
#        print(f"-{p}-")
#        print(prov.loc[prov[prov_col] == p])
#        print("---")
            df.loc[
                df[df_col] == p,
                replace_cols
            ] = prov.loc[prov[prov_col] == p][replace_with].values[0]

    columns = ["province id origin", "region id origin",
               "province id destination", "region id destination"]

    df[columns] = df[columns].fillna(value=0).astype("int8")


#def convert(filename, cell):
#    df = pandas.read_csv(
#        filename,
#        sep=";",
#        encoding="ISO-8859-1"
#    )
#    df.columns = [c.lower().strip() for c in df.columns]
#
#    cell = cell.lower()
#
#    map_ine_cells_to_provinces(df, cell)
#
#    cols = ["province", "province id"]
#    for c in df.columns:
#        if c.startswith("unnamed") or c in cols:
#            continue
#        cols.append(c)
#
#    df = df[cols]
#
#    return df


def aggregate_by_province(df):
    agg = {
        "province id origin": max,
        "province id destination": max,
        "flux": sum
    }
    grouped = df.groupby(
        ["province origin", "province destination"]
    ).aggregate(agg).reset_index()

    sel = grouped["province origin"] == grouped["province destination"]
    df_intra = grouped.loc[sel]
    df_intra = df_intra[["province origin", "province id origin", "flux"]]
    df_intra.columns = ["province", "province id", "flux"]
    df_intra = df_intra.reset_index(drop=True)
#    print("-")
#    print(df_intra.head())
#    print("-")

    sel = grouped["province origin"] != grouped["province destination"]
    df_inter = grouped.loc[sel]
    df_inter.columns = [
        "province origin",
        "province destination",
        "province id origin",
        "province id destination",
        "flux"
    ]
    df_inter = df_inter.reset_index(drop=True)
#    print("-")
#    print(df_inter.head())
#    print("-")
    return df_intra, df_inter


def sort_columns(df):
    # Sort columns, putting geographical information first
    aux = [
        "date",
        "region",
        "region origin",
        "region id origin",
        "region destination",
        "region id destination",
        "province",
        "province origin",
        "province id origin",
        "province destination",
        "province id destination",
        "area",
        "area origin",
        "area id origin",
        "area destination",
        "area id destination",
        "municipality",
        "municipality origin",
        "municipality id origin",
        "municipality destination",
        "municipality id destination",
    ]
    cols = [c for c in aux if c in df.columns]

    for c in df.columns:
        if c.startswith("unnamed") or c in cols:
            continue
        cols.append(c)
    df = df[cols]
    return df


def convert_covid_flux(filename, ocell, dcell):
    df = pandas.read_csv(
        filename,
        sep=";",
        encoding="ISO-8859-1",
        header=0,
        usecols=[0, 1, 2, 3, 4],
        names=['area id origin',
               'area origin',
               'area id destination',
               'area destination',
               'flux']
        )

    ocell = ocell.lower()
    dcell = dcell.lower()

    map_ine_cells_to_provinces(df, ocell, dcell)
    add_province_and_region_data(df, search_by_id=True)
    df = sort_columns(df)

    df_intra, df_inter = aggregate_by_province(df)
    df_intra = sort_columns(df_intra)
    df_inter = sort_columns(df_inter)

    return df, df_intra, df_inter


def convert_ine_flux(filename):
    df = pandas.read_excel(
        filename,
        names=[
            "region origin",
            "province origin",
            "area id origin",
            "area origin",
            "region destination",
            "province destination",
            "area id destination",
            "area destination",
            "flux"
        ]
    )
    add_province_and_region_data(df, search_by_id=False)
    df = sort_columns(df)

    df_intra, df_inter = aggregate_by_province(df)
    df_intra = sort_columns(df_intra)
    df_inter = sort_columns(df_inter)

    return df, df_intra, df_inter


def do_covid():
    print("Transforming cell data into provinces...")

    agg_flux = []
    agg_flux_intra = []
    agg_flux_inter = []
    for d, _, files in os.walk(PATHS.outdir):
        if not d.endswith("original"):
            continue
        d = pathlib.Path(d)

        print(f"\tProcessing '{d}'...")

        for f in files:
            aux = d / f

            if f.startswith("Flujos+15"):
                ocell = "area id origin"
                dcell = "area id destination"
                df, df_intra, df_inter = convert_covid_flux(
                    aux,
                    ocell,
                    dcell,
                )

                date = pandas.to_datetime(d.parent.name)

                df.insert(0, "date", date)
                agg_flux.append(df)

                df_intra.insert(0, "date", date)
                agg_flux_intra.append(df_intra)

                df_inter.insert(0, "date", date)
                agg_flux_inter.append(df_inter)

                aux = d.parent / "province_flux"
                print(f"\t saving to '{aux}'")
                aux.mkdir()
                df.to_csv(aux / "flux.csv", index=False)
                df_inter.to_csv(aux / "flux_inter.csv", index=False)
                df_intra.to_csv(aux / "flux_intra.csv", index=False)

    print(f"Saving concatenated data to {PATHS.outdir}")
    df = pandas.concat(agg_flux)
    df = df.sort_values(["date", "province origin"]).reset_index(drop=True)
    df.to_csv(PATHS.outdir / "province_flux.csv", index=False)

    df = pandas.concat(agg_flux_intra)
    df = df.sort_values(["date", "province"]).reset_index(drop=True)
    df.to_csv(PATHS.outdir / "province_flux_intra.csv", index=False)

    df = pandas.concat(agg_flux_inter)
    df = df.sort_values(["date", "province origin"]).reset_index(drop=True)
    df.to_csv(PATHS.outdir / "province_flux_inter.csv", index=False)


def do_mobility():
    print("Transforming cell data into provinces...")

    agg_flux = []
    agg_flux_intra = []
    agg_flux_inter = []
    for d, _, files in os.walk(PATHS.outdir):
        if not d.endswith("original"):
            continue
        d = pathlib.Path(d)

        print(f"\tProcessing '{d}'...")

        for f in files:
            aux = d / f

            if f.startswith("Tabla 1.3"):
                df, df_intra, df_inter = convert_ine_flux(aux)

                date = pandas.to_datetime(d.parent.name)

                df.insert(0, "date", date)
                agg_flux.append(df)

                df_intra.insert(0, "date", date)
                agg_flux_intra.append(df_intra)

                df_inter.insert(0, "date", date)
                agg_flux_inter.append(df_inter)

                aux = d.parent / "province_flux"
                print(f"\t saving to '{aux}'")
                aux.mkdir()
                df.to_csv(aux / "flux.csv", index=False)
                df_inter.to_csv(aux / "flux_inter.csv", index=False)
                df_intra.to_csv(aux / "flux_intra.csv", index=False)

    print(f"Saving concatenated data to {PATHS.outdir}")
    df = pandas.concat(agg_flux)
    df = df.sort_values(["date", "province origin"]).reset_index(drop=True)
    df.to_csv(PATHS.outdir / "province_flux.csv", index=False)

    df = pandas.concat(agg_flux_intra)
    df = df.sort_values(["date", "province"]).reset_index(drop=True)
    df.to_csv(PATHS.outdir / "province_flux_intra.csv", index=False)

    df = pandas.concat(agg_flux_inter)
    df = df.sort_values(["date", "province origin"]).reset_index(drop=True)
    df.to_csv(PATHS.outdir / "province_flux_inter.csv", index=False)
