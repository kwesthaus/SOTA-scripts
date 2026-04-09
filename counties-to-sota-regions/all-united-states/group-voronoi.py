#!/usr/bin/env python

# e.g. ./group-voronoi.py ./cb_2024_us_county_5m.geojson ~/Downloads/sota-temp/summitslist_ALL-USA_2026-03-17.csv ./group-voronoi.geojso

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

    # new and old
    # {'identifier': 'W6', 'regions': [['CT'], ['CN', 'NE'], ['CC', 'NW', 'NC', 'SC'], ['SN', 'NS', 'SS'], ['CD', 'ND', 'SD', 'IN', 'WH'], ['CV']], 'boundary': {'type': 'state', 'state': 'CA'} },
    # old/unique only
    # {'identifier': 'W6', 'regions': [['CT'], ['CN'], ['CC'], ['SN'], ['CD'], ['CV']], 'boundary': {'type': 'state', 'state': 'CA'} },
    # new/unique only
    # {'identifier': 'W6', 'regions': [['CT'], ['NE'], ['NW', 'NC', 'SC'], ['NS', 'SS'], ['ND', 'SD', 'IN', 'WH'], ['CV']], 'boundary': {'type': 'state', 'state': 'CA'} },

    # new/unique, ignoring CT
    # {'identifier': 'W6', 'regions': [['NE'], ['NW', 'NC', 'SC'], ['NS', 'SS'], ['ND', 'SD', 'IN', 'WH'], ['CV']], 'boundary': {'type': 'state', 'state': 'CA'} },

    # physiography, others are overlay NE      CC                        SN      CD      CV
    # overlay: CT, CN, NW, NC, SC, NS, SS, ND, SD, IN, WH
    # {'identifier': 'W6', 'regions': [['NE'], ['CC', 'NW', 'NC', 'SC'], ['SN'], ['CD'], ['CV']], 'boundary': {'type': 'state', 'state': 'CA'} },






    # CT should be an overlay
    # CN should be an overlay
    # WH and IN should be an overlay
    # CV maybe overlay?
    # sierras and desert annoying boundary
    # - really this is only caused by ND, rest voronoi well together

    # boundaries that are clean:
    # NE and CC (boundary is I-5)
    # NE and NW (boundary is I-5)
    # NE and NC

    # NE and SN
    # NE and NS (boundary is Deer Creek, CA-32, CA-36, US-395 except for 1 dip below)

    # all the coast ones (CC, NW, NC, SC) and all the sierra ones (SN, NS, SS)
    # all the coast ones (CC, NW, NC, SC) and all the desert ones (CD, ND, SD)

    # CV does not voronoi well
    # CT does not voronoi well





    # ND and SD overlap, CD overlaps both
    # ND and NS overlap
    # ND and SS overlap
    # ND and SN voronoi well

    # SD plays well with all sierra
    # CD plays well with all sierra




    # {'identifier': 'W6', 'regions': [['NE'], ['CC', 'NW', 'NC', 'SC'], ['SN', 'NS', 'SS']], 'boundary': {'type': 'state', 'state': 'CA'} },
    # {'identifier': 'W6', 'regions': [['NE'], ['CC', 'NW', 'NC', 'SC'], ['CD', 'ND', 'SD']], 'boundary': {'type': 'state', 'state': 'CA'} },
    # {'identifier': 'W6', 'regions': [['SN', 'NS', 'SS'], ['CD', 'ND', 'SD']], 'boundary': {'type': 'state', 'state': 'CA'} },

    {
        'identifier': 'W6',
        'boundarydef': {'type': 'state', 'state': 'CA'},
        'groups': [
            {'regions': ['NE'],                     'entire': 'NE'}, 
            {'regions': ['CC', 'NW', 'NC', 'SC'],   'entire': 'CC', 'hull': ['NW'], 'voronoi': [
                {'regions': ['NC'], 'entire': 'NC'}, {'regions': ['SC'], 'entire': 'SC'}
            ]},
            {'regions': ['SN', 'NS', 'SS'],         'entire': 'SN', 'voronoi': [
                {'regions': ['NS'], 'entire': 'NS'}, {'regions': ['SS'], 'entire': 'SS'}
            ]},
            {'regions': ['CD', 'SD'],               'entire': 'CD', 'hull': ['SD']}
        ],
    },
    # overlays: CT, CV, CN, WH, IN, ND

    # {'identifier': 'W6', 'regions': [['NS'], ['SS']], 'boundary': {'type': 'state', 'state': 'CA'} },
    # {'identifier': 'W6', 'regions': [['NC'], ['SC']], 'boundary': {'type': 'state', 'state': 'CA'} },

]

def construct_regionstosummits(assoc_id, groups):
    all_regions = []
    for group in groups:
        all_regions.extend([region for region in group['regions']])
    # IMPORTANT: this iteration occurs in the order we originally specified the regions
    for region in all_regions:
        print(region)

        rgrows = []
        def is_region(row):
            sass = row['SummitCode'].split('-')[0]
            sass, sreg = sass.split('/')
            if sass == assoc_id and sreg == region:
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
    return region_summits

def voronoi_in_boundary(groups, regions_to_summits, boundary_shp):
    all_regions = []
    for group in groups:
        all_regions.extend([region for region in group['regions']])
    latlonlist = []
    for region in all_regions:
        # IMPORTANT: this operation preserves order, so that all summits from the same region occur together in one block
        latlonlist.extend([(row['Longitude'], row['Latitude']) for row in region_summits[region]])
    # IMPORTANT: this operation preserves order
    mp = shapely.MultiPoint(latlonlist)
    # IMPORTANT: maintain ordering
    vout = shapely.voronoi_polygons(mp, ordered=True)

    idx = 0
    # IMPORTANT: this iteration occurs in the same order as the first time we iterated through the regions
    for group in groups:
        numsummits = 0
        for region in group['regions']:
            numsummits += len(region_summits[region])
        # IMPORTANT: because we have maintained ordering to this point, we can simply use an index range to collect all individual polygons that belong to a single region
        polygons = vout.geoms[idx:idx+numsummits]
        # dissolve polygons-for-each-summit into minimal polygon (or multi-polygon) for the region
        cov = shapely.coverage_union_all(polygons)
        # typically the resulting voronoi polygons extend out super far, cut them off at the boundary specified for the association
        cov = shapely.intersection(cov, boundary_shp)

        group['shape'] = cov
        idx += numsummits


for ft in cgj["features"]:
    county_name = ft["properties"]["STUSPS"] + "_" + ft["properties"]["NAME"]
    counties_dict[county_name] = ft
    # e.g. { "WA_Grant": {...}, "WA_Clark": {...}, ... }

for assoc_def in voronoi_assocs:
    print()
    print(assoc_def['identifier'])
    counties_list = []
    region_summits = {}

    if "type" in assoc_def['boundarydef'] and assoc_def['boundarydef']['type'] == "state":
        state = assoc_def['boundarydef']['state']
        counties_list = [x for x in counties_dict.keys() if x.split('_')[0] == state]
    else:
        print("don't know how to handle this voronoi assoc, quitting!")
        exit(1)

    blank = {"type": "Polygon", "coordinates": []}
    bnd_shp = shapely.geometry.shape(blank)

    for county_name in counties_list:
        countyshp = shapely.geometry.shape(counties_dict[county_name]["geometry"])
        # print(f"about to merge {region['name']} with {county_name}")
        bnd_shp = shapely.coverage_union(bnd_shp, countyshp)

    region_summits = construct_regionstosummits(assoc_def['identifier'], assoc_def['groups'])

    voronoi_in_boundary(assoc_def['groups'], region_summits, bnd_shp)

    for regiongroup in assoc_def['groups']:
        if 'voronoi' in regiongroup:
            voronoi_in_boundary(regiongroup['voronoi'], region_summits, regiongroup['shape'])
            for subgroup in regiongroup['voronoi']:
                rgft = copy.deepcopy(feature_template)
                rgft["geometry"] = shapely.geometry.mapping(subgroup['shape'])
                rgft["properties"]["identifier"] = assoc_def['identifier'] + '/' + subgroup['entire']
                gj_template["features"].append(rgft)
        if 'hull' in regiongroup:
            for hullrgn in regiongroup['hull']:
                latlonlist = [(row['Longitude'], row['Latitude']) for row in region_summits[hullrgn]]
                hull = shapely.concave_hull(shapely.MultiPoint(latlonlist), ratio=0.6)
                cov = shapely.intersection(hull, regiongroup['shape'])

                rgft = copy.deepcopy(feature_template)
                rgft["geometry"] = shapely.geometry.mapping(cov)
                rgft["properties"]["identifier"] = assoc_def['identifier'] + '/' + hullrgn
                gj_template["features"].append(rgft)


        rgft = copy.deepcopy(feature_template)
        rgft["geometry"] = shapely.geometry.mapping(regiongroup['shape'])
        rgft["properties"]["identifier"] = assoc_def['identifier'] + '/' + regiongroup['entire']
        gj_template["features"].append(rgft)




with open(sys.argv[3], 'w') as outf:
    json.dump(gj_template, outf)

print("done")

