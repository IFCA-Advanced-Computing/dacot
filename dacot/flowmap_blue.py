"""
Add the following to the map url to customize it nicely
?f=13&col=BurgYl&c=0&bo=100

f: fade transparency, c: clustering, col: color, bo: base map transparency

Play with params here:
https://flowmap.blue/1mK1ZMxNmGtSSxMhtoKO5h7nxyDMXFC_3_u4eo4rtucg/ce149d3?v=45.533556,-73.600797,10.87,0,0&a=0&as=1&b=1&bo=100&c=0&ca=1&d=1&fe=1&lt=1&lfm=ALL&col=BurgYl&f=13
"""

import pathlib

import pandas as pd
import requests

base_dir = pathlib.Path('/home/iheredia/ignacio/covid/dacot/data')

em2_dir = base_dir / "output" / "output_em2_20210323-1.0.1.dev8"
em3_dir = base_dir / "output" / "output_em3_20210323-1.0.1.dev8"

# Load flows and create combined dataset if needed
flows = pd.DataFrame([])
for d in [em2_dir, em3_dir]:
    f = pd.read_csv(d / "province_flux.csv")
    flows = pd.concat([flows, f])

# Load coordinates of places
f = base_dir / "output" / "flowmap-blue" / "coord.csv"
if not f.exists():
    lat, lon = [], []
    names = sorted(set(flows['province origin']))
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

    coord = pd.DataFrame({'name': names, 'lat': lat, 'lon': lon})
    coord.to_csv(
        base_dir / "output" / "flowmap-blue" / "coord.csv",
        index=False,
    )
else:
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
