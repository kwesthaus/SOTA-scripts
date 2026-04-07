#!/usr/bin/env python

# e.g. ./voronoi.py ./cb_2024_us_county_5m.geojson ~/Downloads/sota-temp/summitslist_ALL-USA_2026-03-17.csv ./voronoi.geojso

import sys
import json
import copy
import shapely
import shapely.ops
import csv
import datetime

# geojson that I converted from census.gov carto boundary .shp file
with open(sys.argv[1], 'r') as cf:
    cgj = json.load(cf)

gj_template = {
    "type": "FeatureCollection",
    "name": "United States SOTA Regions",
    "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
    "features": [],
}

feature_template = {
    "type": "Feature",
    "properties": {},
    "geometry": {"type": "Polygon", "coordinates": []},
}

counties_dict = {}


'''

regions = [

    # W6: 16 regions, 58 counties
    # Original 5 regions: Northern Ranges, Coastal Ranges, Sierra Nevada, Transverse Ranges, Desert Ranges
    # New regions overlap 4 of the 5 existing regions (all except Transverse Ranges), and Central Valley covers new area
    # Voronoi with the old regions+Central Valley, hull the other new regions? or Voronoi new, hull old?
    {'identifier': 'W6/CT', 'name': 'Transverse Ranges',       'type': 'concave-hull' },

    {'identifier': 'W6/CN', 'name': 'Northern Ranges',         'type': 'concave-hull' },
    {'identifier': 'W6/NE', 'name': 'Northeastern Ranges',     'type': 'concave-hull' },

    {'identifier': 'W6/CC', 'name': 'Coastal Ranges',          'type': 'concave-hull' },
    {'identifier': 'W6/NW', 'name': 'Northwestern Ranges',     'type': 'concave-hull' },
    {'identifier': 'W6/NC', 'name': 'Northern Coastal Ranges', 'type': 'concave-hull' },
    {'identifier': 'W6/SC', 'name': 'Southern Coastal Ranges', 'type': 'concave-hull' },

    {'identifier': 'W6/SN', 'name': 'Sierra Nevada',           'type': 'concave-hull' },
    {'identifier': 'W6/NS', 'name': 'Northern Sierra',         'type': 'concave-hull' },
    {'identifier': 'W6/SS', 'name': 'Southern Sierra',         'type': 'concave-hull' },

    {'identifier': 'W6/CD', 'name': 'Desert Ranges',           'type': 'concave-hull' },
    {'identifier': 'W6/ND', 'name': 'Northern Desert',         'type': 'concave-hull' },
    {'identifier': 'W6/SD', 'name': 'Southern Desert',         'type': 'concave-hull' },
    {'identifier': 'W6/IN', 'name': 'Inyo Mountains',          'type': 'concave-hull' },
    {'identifier': 'W6/WH', 'name': 'White Mountains',         'type': 'concave-hull' },

    {'identifier': 'W6/CV', 'name': 'Central Valley',          'type': 'concave-hull' },

]

'''

voronoi_assocs = [

    # {'identifier': 'W6', 'regions': ['CT', 'CN', 'CC', 'SN', 'CD', 'CV'], 'boundary': {'type': 'state', 'state': 'CA'} },
    # {'identifier': 'W6', 'regions': ['CT', 'NE', 'NW', 'NC', 'SC', 'NS', 'SS', 'ND', 'SD', 'IN', 'WH', 'CV'], 'boundary': {'type': 'state', 'state': 'CA'} },

    {'identifier': 'W5A', 'regions': ['BR', 'CA', 'CS', 'MA', 'OA', 'OH', 'OZ', 'PT'], 'boundary': {'type': 'counties', 'counties': ['AR_Benton', 'AR_Carroll', 'AR_Boone', 'AR_Newton', 'AR_Madison', 'AR_Searcy', 'AR_Stone', 'AR_Izard', 'AR_Franklin', 'AR_Johnson', 'AR_Van Buren', 'AR_Pope', 'AR_Conway', 'AR_Yell', 'AR_Logan', 'AR_Pulaski', 'AR_Saline', 'AR_Perry', 'AR_Sebastian', 'AR_Scott', 'AR_Garland', 'AR_Montgomery', 'AR_Polk', 'AR_Pike']} },

    {'identifier': 'W5O', 'regions': ['QA', 'WI'], 'boundary': {'type': 'counties', 'counties': ['OK_Greer', 'OK_Kiowa', 'OK_Jackson', 'OK_Comanche']} },
    {'identifier': 'W5O', 'regions': ['BS', 'KI', 'OU', 'SO', 'WO'], 'boundary': {'type': 'counties', 'counties': ['OK_Murray', 'OK_Pontotoc', 'OK_Adair', 'OK_Cherokee', 'OK_Sequoyah', 'OK_Muskogee', 'OK_Haskell', 'OK_Pittsburg', 'OK_Latimer', 'OK_Le Flore', 'OK_Atoka', 'OK_Pushmataha', 'OK_McCurtain']} },

    {'identifier': 'W5T', 'regions': ['BG', 'BO', 'CE', 'CH', 'CI', 'CR', 'DE', 'DH', 'DN', 'DW', 'EA', 'EF', 'FR', 'GL', 'GU', 'HA', 'PB', 'PU', 'QU', 'SB', 'SD', 'SN', 'SV', 'VH'], 'boundary': {'type': 'counties', 'counties': ['TX_El Paso', 'TX_Hudspeth', 'TX_Culberson', 'TX_Jeff Davis', 'TX_Presidio', 'TX_Brewster', 'TX_Pecos']} },

    {'identifier': 'W5N', 'regions': ['AI', 'AP', 'BA', 'BL', 'BU', 'CB', 'CC', 'CD', 'CM', 'CN', 'CO', 'CU', 'DA', 'EL', 'FL', 'GF', 'GW', 'HT', 'MG', 'MI', 'MO', 'NL', 'OR', 'OT', 'PA', 'PL', 'PO', 'PW', 'RO', 'SC', 'SE', 'SG', 'SI', 'SL', 'SM', 'SR', 'SS'], 'boundary': {'type': 'counties', 'counties': ['NM_San Juan', 'NM_Rio Arriba', 'NM_Sandoval', 'NM_McKinley', 'NM_Cibola', 'NM_Bernalillo', 'NM_Valencia', 'NM_Catron', 'NM_Socorro', 'NM_Sierra', 'NM_Grant', 'NM_Hidalgo', 'NM_Luna', 'NM_Doña Ana', 'NM_Otero', 'NM_Chaves', 'NM_Lincoln', 'NM_Torrance', 'NM_Los Alamos', 'NM_Santa Fe', 'NM_Taos', 'NM_Colfax', 'NM_Union', 'NM_Harding', 'NM_Mora', 'NM_San Miguel', 'NM_Guadalupe', 'NM_Quay', 'NM_Eddy']} },

    {'identifier': 'W7O', 'regions': ['CC', 'CE', 'CM', 'CN', 'CS', 'NC', 'NE', 'SC', 'SE', 'WV'], 'boundary': {'type': 'state', 'state': 'OR'} },

    {'identifier': 'W0C', 'regions': ['FR', 'LG', 'MZ', 'PR', 'RG', 'RP', 'SC', 'SJ', 'SL', 'SM', 'SP', 'SR', 'UR', 'WE'], 'boundary': {'type': 'counties', 'counties': ['CO_Moffat', 'CO_Rio Blanco', 'CO_Garfield', 'CO_Mesa', 'CO_Delta', 'CO_Montrose', 'CO_San Miguel', 'CO_Dolores', 'CO_Montezuma', 'CO_La Plata', 'CO_Archuleta', 'CO_Ouray', 'CO_San Juan', 'CO_Hinsdale', 'CO_Gunnison', 'CO_Pitkin', 'CO_Eagle', 'CO_Routt', 'CO_Jackson', 'CO_Grand', 'CO_Summit', 'CO_Lake', 'CO_Chaffee', 'CO_Saguache', 'CO_Mineral', 'CO_Rio Grande', 'CO_Conejos', 'CO_Alamosa', 'CO_Costilla', 'CO_Las Animas', 'CO_Huerfano', 'CO_Custer', 'CO_Pueblo', 'CO_Fremont', 'CO_Park', 'CO_Clear Creek', 'CO_Gilpin', 'CO_Boulder', 'CO_Larimer', 'CO_Jefferson', 'CO_Douglas', 'CO_Teller', 'CO_El Paso']} },

    {'identifier': 'W1', 'regions': ['AM', 'EM', 'DI'], 'boundary': {'type': 'state', 'state': 'ME'} },
    {'identifier': 'W1', 'regions': ['HA', 'NL', 'MV'], 'boundary': {'type': 'state', 'state': 'NH'} },
    {'identifier': 'W1', 'regions': ['GM', 'NK'], 'boundary': {'type': 'state', 'state': 'VT'} },
    {'identifier': 'W1', 'regions': ['MB', 'CR'], 'boundary': {'type': 'state', 'state': 'MA'} },
    {'identifier': 'W1', 'regions': ['CB', 'MR', 'HH'], 'boundary': {'type': 'state', 'state': 'CT'} },

]

for ft in cgj["features"]:
    county_name = ft["properties"]["STUSPS"] + "_" + ft["properties"]["NAME"]
    counties_dict[county_name] = ft
    # e.g. { "WA_Grant": {...}, "WA_Clark": {...}, ... }

for assoc in voronoi_assocs:
    print()
    print(assoc['identifier'])
    counties_list = []
    region_summits = {}

    if "type" in assoc['boundary'] and assoc['boundary']['type'] == "state":
        state = assoc['boundary']['state']
        counties_list = [x for x in counties_dict.keys() if x.split('_')[0] == state]
    elif "type" in assoc['boundary'] and assoc['boundary']['type'] == "counties":
        counties_list = assoc['boundary']['counties']
    else:
        print("don't know how to handle this voronoi assoc, quitting!")
        exit(1)

    blank = {"type": "Polygon", "coordinates": []}
    bnd_shp = shapely.geometry.shape(blank)

    for county_name in counties_list:
        countyshp = shapely.geometry.shape(counties_dict[county_name]["geometry"])
        # print(f"about to merge {region['name']} with {county_name}")
        bnd_shp = shapely.coverage_union(bnd_shp, countyshp)

    latlonlist = []
    # IMPORTANT: this iteration occurs in the order we originally specified the regions
    for region in assoc['regions']:
        print(region)
        rgrows = []
        def is_region(row):
            sass = row['SummitCode'].split('-')[0]
            sass, sreg = sass.split('/')
            if sass == assoc['identifier'] and sreg == region:
                vf = datetime.date.strptime(row['ValidFrom'], "%d/%m/%Y")
                vt = datetime.date.strptime(row['ValidTo'], "%d/%m/%Y")
                dt = datetime.date.today()
                return dt < vt and dt > vf
            return False
        with open(sys.argv[2], 'r') as sf:
            rd = csv.DictReader(sf)

            for row in filter(is_region, rd):
                # print(row['SummitCode'])
                rgrows.append(row)
        region_summits[region] = rgrows

        # IMPORTANT: this operation preserves order, so that all summits from the same region occur together in one block
        latlonlist.extend([(row['Longitude'], row['Latitude']) for row in rgrows])

    # IMPORTANT: this operation preserves order
    mp = shapely.MultiPoint(latlonlist)
    
    # IMPORTANT: maintain ordering
    vout = shapely.voronoi_polygons(mp, ordered=True)

    idx = 0
    # IMPORTANT: this iteration occurs in the same order as the first time we iterated through the regions
    for region in assoc['regions']:
        numsummits = len(region_summits[region])
        # IMPORTANT: because we have maintained ordering to this point, we can simply use an index range to collect all individual polygons that belong to a single region
        polygons = vout.geoms[idx:idx+numsummits]
        # dissolve polygons-for-each-summit into minimal polygon (or multi-polygon) for the region
        cov = shapely.coverage_union_all(polygons)
        # typically the resulting voronoi polygons extend out super far, cut them off at the boundary specified for the association
        cov = shapely.intersection(cov, bnd_shp)

        rgft = copy.deepcopy(feature_template)
        rgft["geometry"] = shapely.geometry.mapping(cov)
        rgft["properties"]["identifier"] = assoc['identifier'] + '/' + region
        gj_template["features"].append(rgft)

        idx += numsummits



with open(sys.argv[3], 'w') as outf:
    json.dump(gj_template, outf)

print("done")

