"""
Add the following to the map url to customize it nice
?f=13&col=BurgYl&c=0&bo=100

f: fade transparency, c: clustering, col: color, bo: base map transparency

Play with params here:
https://flowmap.blue/1mK1ZMxNmGtSSxMhtoKO5h7nxyDMXFC_3_u4eo4rtucg/ce149d3?v=45.533556,-73.600797,10.87,0,0&a=0&as=1&b=1&bo=100&c=0&ca=1&d=1&fe=1&lt=1&lfm=ALL&col=BurgYl&f=13
"""

import pathlib

import pandas as pd
import requests

base_dir = pathlib.Path('/home/iheredia/ignacio/covid/dacot/data')

# Load flows

flows_intra = pd.read_csv(
    base_dir / "output" / "output_em2_20210224-1.0.1.dev4" / "province_flux_intra.csv"
)
flows_inter = pd.read_csv(
    base_dir / "output" / "output_em2_20210224-1.0.1.dev4" / "province_flux_inter.csv"
)

flows_intra['province destination'] = flows_intra['province']
flows_intra['province id destination'] = flows_intra['province id']
flows_intra = flows_intra.rename(columns={'province': 'province origin',
                                          'province id': 'province id origin'})

flows = pd.concat([flows_inter, flows_intra])

# Create coordinates file for locations


def create_coord_file():
    names = sorted(set(flows['province origin']))

    lat, lon = [], []
    for province in names:
        url = 'https://nominatim.openstreetmap.org/search'
        if province in ['Ceuta', 'Melilla']:
            params = {'city': province, 'country': 'spain', 'format': 'json'}
        else:
            params = {'county': province, 'country': 'spain', 'format': 'json'}
        r = requests.get(url, params=params)
        r = r.json()[0]
        lat.append(r['lat'])
        lon.append(r['lon'])

    df = pd.DataFrame({'name': names, 'lat': lat, 'lon': lon})
    df.to_csv(
        base_dir / "output" / "flowmap-blue" / "coord.csv",
        index=False,
    )


f = base_dir / "output" / "flowmap-blue" / "coord.csv"
if not f:
    create_coord_file()
coord = pd.read_csv(f)

# Save locations
locations = flows.groupby(['province origin', 'province id origin']).size().reset_index()
locations = locations.drop(0, axis=1)
locations = locations.rename(columns={"province origin": "name", "province id origin": "id"})
locations = locations.merge(coord)
locations = locations[['id', 'name', 'lat', 'lon']]

locations.to_csv(
    base_dir / "output" / "flowmap-blue" / "locations.csv",
    index=False,
)

# Save flows
flows = flows.rename(columns={"province id origin": "origin",
                              "province id destination": "dest",
                              "flux": "count",
                              "date": "time"})
flows = flows.drop(['province origin', 'province destination'], axis=1)

# Remove lonely date
flows = flows[flows.time != '2019-11-01']

flows.to_csv(
    base_dir / "output" / "flowmap-blue" / "flows.csv",
    index=False,
)
