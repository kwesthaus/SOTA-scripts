#!/usr/bin/env python

import sys
import json
import copy
import shapely

# https://data-wadnr.opendata.arcgis.com/datasets/wa-county-boundaries/explore
with open(sys.argv[1], 'r') as inf:
    gj = json.load(inf)

gj_template = {
    "type": "FeatureCollection",
    "name": "W7W Regions",
    "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
    "features": [],
}

feature_template = {
    "type": "Feature",
    "properties": {},
    "geometry": {"type": "Polygon", "coordinates": []},
}

counties_dict = {}

regions = [
    {'identifier': 'CH', 'name': 'WA-Chelan',               'counties': ['Chelan'] },
    {'identifier': 'CW', 'name': 'WA-Central Washington',   'counties': ['Kittitas', 'Grant', 'Douglas'] },
    {'identifier': 'FR', 'name': 'WA-Ferry',                'counties': ['Ferry'] },
    {'identifier': 'KG', 'name': 'WA-King',                 'counties': ['King'] },
    {'identifier': 'LC', 'name': 'WA-Lower Columbia',       'counties': ['Clark', 'Cowlitz', 'Skamania', 'Wahkiakum'] },
    {'identifier': 'MC', 'name': 'WA-Middle Columbia',      'counties': ['Yakima', 'Klickitat'] },
    {'identifier': 'NO', 'name': 'WA-Northern Olympics',    'counties': ['Clallam', 'Jefferson'] },
    {'identifier': 'OK', 'name': 'WA-Okanogan',             'counties': ['Okanogan'] },
    {'identifier': 'PL', 'name': 'WA-Pacific-Lewis',        'counties': ['Pacific', 'Lewis'] },
    {'identifier': 'PO', 'name': 'WA-Pend Oreille',         'counties': ['Pend Oreille'] },
    {'identifier': 'RS', 'name': 'WA-Rainier-Salish',       'counties': ['Island', 'Kitsap', 'Pierce', 'San Juan'] },
    {'identifier': 'SK', 'name': 'WA-Skagit',               'counties': ['Skagit'] },
    {'identifier': 'SN', 'name': 'WA-Snohomish',            'counties': ['Snohomish'] },
    {'identifier': 'SO', 'name': 'WA-Southern Olympics',    'counties': ['Grays Harbor', 'Mason', 'Thurston'] },
    {'identifier': 'ST', 'name': 'WA-Stevens',              'counties': ['Stevens'] },
    {'identifier': 'WE', 'name': 'WA-Washington East',      'counties': ['Adams', 'Asotin', 'Benton', 'Columbia', 'Franklin', 'Garfield', 'Lincoln', 'Spokane', 'Walla Walla', 'Whitman'] },
    {'identifier': 'WH', 'name': 'WA-Whatcom',              'counties': ['Whatcom'] },
]

for ft in gj["features"]:
    counties_dict[ft["properties"]["JURISDICT_LABEL_NM"]] = ft
    # e.g. { "Grant": {...}, "Clark": {...}, ... }

for region in regions:
    rgft = copy.deepcopy(feature_template)
    rgft["properties"] = region
    for county_name in region["counties"]:
        rgjson = json.dumps(rgft["geometry"])
        rgshp = shapely.from_geojson(rgjson)
        countyjson = json.dumps(counties_dict[county_name]["geometry"])
        countyshp = shapely.from_geojson(countyjson)
        mergedshp = shapely.coverage_union(rgshp, countyshp)
        rgft["geometry"] = shapely.geometry.mapping(mergedshp)
    gj_template["features"].append(rgft)

with open(sys.argv[2], 'w') as outf:
    json.dump(gj_template, outf)

print("done")

