#!/usr/bin/env python

# e.g. ./colorize-regions.py ./all-united-states/w-regions.geojson ./my-chased-regions.json ./my-colored-regions.geojson

import sys
import json

if len(sys.argv) < 4:
    print('regfile chasedfile outfile')
    exit(1)

with open(sys.argv[1], 'r') as regfile:
    regj = json.load(regfile)

# https://www.sotadata.org.uk/en/logs/chaser/regions
# https://api-db2.sota.org.uk//logs/regions/chaser/-1
with open(sys.argv[2], 'r') as chasedfile:
    chasedj = json.load(chasedfile)

chasedset = set()
# TODO parse from summitslist.csv instead of hardcode
neveractive = {'W8V/NP', 'W0N/SH', 'W5T/BG', 'W5T/CE', 'W5T/CH', 'W5T/DN', 'W5T/EA', 'W5T/GL', 'W5T/HA', 'W5T/PB', 'W5T/PU', 'W5T/QU', 'W5T/SD', 'W5T/SV', 'W5T/VH', 'W5N/SR'}

regionalerted = {'W0D/ND', 'W6/CV', 'W6/ND', 'W6/NW', 'W6/SN', 'W6/WH', 'W7I/BL', 'W7I/CU', 'W7I/IC', 'W7I/LE', 'W7I/NI', 'W7I/NP', 'W7I/SR', 'W7I/VC', 'W7M/BR', 'W7M/CL', 'W7M/FN', 'W7M/GA', 'W7M/GR', 'W7M/NF', 'W7M/PN', 'W7M/PS', 'W7M/SF', 'W7N/EL', 'W7N/EM', 'W7N/EN', 'W7N/ES', 'W7N/HU', 'W7N/LN', 'W7N/NN', 'W7N/NS', 'W7N/PC', 'W7N/WP', 'W7O/SE', 'W7Y/EW', 'W7Y/FT', 'W7Y/NW', 'W7Y/PA', 'W7Y/SL', 'W7Y/TT', 'W7U/BE', 'W7U/BO', 'W7U/CA', 'W7U/CR', 'W7U/DA', 'W7U/DU', 'W7U/DV', 'W7U/EM', 'W7U/GA', 'W7U/GR', 'W7U/IR', 'W7U/JU', 'W7U/KA', 'W7U/MI', 'W7U/MO', 'W7U/NU', 'W7U/PI', 'W7U/RI', 'W7U/SE', 'W7U/SJ', 'W7U/SL', 'W7U/SM', 'W7U/SP', 'W7U/SU', 'W7U/TO', 'W7U/UI', 'W7U/WA', 'W7U/WB', 'W7U/WS', 'W7U/WY', 'W7A/AE', 'W7A/CO', 'W7A/GI', 'W7A/GM', 'W7A/GR', 'W7A/MN', 'W7A/MS', 'W7A/NA', 'W7A/NM', 'W7A/PN', 'W7A/PW', 'W7A/PZ', 'W7A/SC', 'W7A/SM', 'W7A/YU', 'W7A/YV'}
assocalerted = {'W0I', 'W0M', 'W5A', 'W5M', 'W5O', 'W8M', 'W8O', 'W8V', 'W9'}

for chasedreg in chasedj:
    chasedset.add(chasedreg['Region'])

gj_template = {
    "type": "FeatureCollection",
    "name": "United States SOTA Regions",
    "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
    "features": [],
}

for rgft in regj['features']:
    colored = False
    if rgft['properties']['identifier'] in chasedset:
        colored = True
        # yellow
        rgft['properties']['stroke'] = '#006000'
        rgft['properties']['stroke-width'] = 2
        rgft['properties']['stroke-opacity'] = 1
        rgft['properties']['fill'] = '#00c000'
        rgft['properties']['fill-opacity'] = 0.5
    if rgft['properties']['identifier'] in neveractive:
        if colored:
            print(f"{rgft['properties']['identifier']} already colored!")
            exit(1)
        colored = True
        # red
        rgft['properties']['stroke'] = '#3f0000'
        rgft['properties']['stroke-width'] = 2
        rgft['properties']['stroke-opacity'] = 1
        rgft['properties']['fill'] = '#7f0000'
        rgft['properties']['fill-opacity'] = 0.5
    if rgft['properties']['identifier'] in regionalerted:
        if colored:
            print(f"{rgft['properties']['identifier']} already colored!")
            exit(1)
        colored = True
        # blue
        rgft['properties']['stroke'] = '#000060'
        rgft['properties']['stroke-width'] = 2
        rgft['properties']['stroke-opacity'] = 1
        rgft['properties']['fill'] = '#0000c0'
        rgft['properties']['fill-opacity'] = 0.5
    if rgft['properties']['identifier'].split('/')[0] in assocalerted:
        if colored:
            print(f"{rgft['properties']['identifier']} already colored, ignoring association")
        else:
            colored = True
            # purple
            rgft['properties']['stroke'] = '#402050'
            rgft['properties']['stroke-width'] = 2
            rgft['properties']['stroke-opacity'] = 1
            rgft['properties']['fill'] = '#8040a0'
            rgft['properties']['fill-opacity'] = 0.5

    gj_template['features'].append(rgft)

with open(sys.argv[3], 'w') as outf:
    json.dump(gj_template, outf)

print('done')

