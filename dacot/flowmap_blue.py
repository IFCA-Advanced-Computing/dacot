import pathlib

import pandas as pd


base_dir = pathlib.Path('/home/iheredia/ignacio/covid/dacot/data')

flows = provinces = pd.read_csv(
    base_dir / "output" / "output_em2_20210224-1.0.1.dev4" / "province_flux_inter.csv"
)

# Save locations
# Add coordinates afterwards using https://flowmap.blue/geocoding
locations = flows.groupby(['province origin', 'province id origin']).size().reset_index()
locations = locations.drop(0, axis=1)
locations = locations.rename(columns={"province origin": "name", "province id origin": "id"})

f = base_dir / "output" / "flowmap-blue" / "locations-no_coord.csv"
locations.to_csv(
    f,
    index=False,
)

# Save flows
flows = flows.rename(columns={"province id origin": "origin",
                              "province id destination": "dest",
                              "flux": "count",
                              "date": "time"})
flows = flows.drop(['province origin', 'province destination'], axis=1)

f = base_dir / "output" / "flowmap-blue" / "flows.csv"
flows.to_csv(
    f,
    index=False,
)
