#!/usr/bin/env python

# e.g. ./convert-all-w.py ./cb_2024_us_county_5m.geojson ~/Downloads/sota-temp/summitslist_ALL-USA_2026-03-17.csv ./w-regions.geojson

# TODO log/print which polygons have holes and which are multipolygons
# TODO maybe switch from concave hull to voronoi+dissolve? this would fix overlapping by making multipolygons

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


# 35 SOTA regions in United States covering 45 states
# no summits (5): Kansas, Louisiana, Florida, Delaware, Rhode Island

## CALL AREAS - 1 BIG REGION
# 1st call district: 6 states (5 with summits), 1 region
# 2nd call district: 2 states, 1 region
# 3rd call district: 3 states (2 with summits), 1 region
# 9th call district: 3 states, 1 region

## CALL AREAS - EACH STATE OWN REGION
# 5th call district: 6 states (5 with summits), 5 regions
# 6th call district: 1 state, 1 region
# 7th call district: 8 states, 8 regions
# 8th call district: 3 states, 3 regions
# KLA, KLF, KLS
# KH6

## CALL AREAS - MIX OF BOTH
# 0th call district: 8 states (7 with summits), 6 regions
# 4th call district: 8 states (7 with summits), 6 regions









# 2 todo, 25 work with counties, 8 special

## (2) TODO
# KLA/KLF/KLS
# KH6

## (19) ARM lists counties in region description or has county-based region map in ARM
# W3
# W9
# W0N
# W4K
# W4A
# W4G
# W4T
# W4V
# W4C
# W7N
# W7U
# W7A
# W7W
# W7Y
# W7I
# W7M
# W8O
# W8V
# W8M

## (3) ARM shows counties in summit table, and seems county based
# K0M
# W0D
# W0M

## (4) ARM shows counties in summit table, but does NOT seem county based
# W5A
# W5N
# W5O
# W5T

## (3) ARM doesn't mention counties, but seems county based
# W2
# W0I
# W5M

## (4) not county based
# W1
# W7O
# W0C
# W6



regions = [

    # W7W: 17 regions, 39 counties
    # counties not in any region: (none)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W7W/CH', 'name': 'WA-Chelan',                   'counties': ['WA_Chelan'] },
    {'identifier': 'W7W/CW', 'name': 'WA-Central Washington',       'counties': ['WA_Kittitas', 'WA_Grant', 'WA_Douglas'] },
    {'identifier': 'W7W/FR', 'name': 'WA-Ferry',                    'counties': ['WA_Ferry'] },
    {'identifier': 'W7W/KG', 'name': 'WA-King',                     'counties': ['WA_King'] },
    {'identifier': 'W7W/LC', 'name': 'WA-Lower Columbia',           'counties': ['WA_Clark', 'WA_Cowlitz', 'WA_Skamania', 'WA_Wahkiakum'] },
    {'identifier': 'W7W/MC', 'name': 'WA-Middle Columbia',          'counties': ['WA_Yakima', 'WA_Klickitat'] },
    {'identifier': 'W7W/NO', 'name': 'WA-Northern Olympics',        'counties': ['WA_Clallam', 'WA_Jefferson'] },
    {'identifier': 'W7W/OK', 'name': 'WA-Okanogan',                 'counties': ['WA_Okanogan'] },
    {'identifier': 'W7W/PL', 'name': 'WA-Pacific-Lewis',            'counties': ['WA_Pacific', 'WA_Lewis'] },
    {'identifier': 'W7W/PO', 'name': 'WA-Pend Oreille',             'counties': ['WA_Pend Oreille'] },
    {'identifier': 'W7W/RS', 'name': 'WA-Rainier-Salish',           'counties': ['WA_Island', 'WA_Kitsap', 'WA_Pierce', 'WA_San Juan'] },
    {'identifier': 'W7W/SK', 'name': 'WA-Skagit',                   'counties': ['WA_Skagit'] },
    {'identifier': 'W7W/SN', 'name': 'WA-Snohomish',                'counties': ['WA_Snohomish'] },
    {'identifier': 'W7W/SO', 'name': 'WA-Southern Olympics',        'counties': ['WA_Grays Harbor', 'WA_Mason', 'WA_Thurston'] },
    {'identifier': 'W7W/ST', 'name': 'WA-Stevens',                  'counties': ['WA_Stevens'] },
    {'identifier': 'W7W/WE', 'name': 'WA-Washington East',          'counties': ['WA_Asotin', 'WA_Benton', 'WA_Columbia', 'WA_Franklin', 'WA_Garfield', 'WA_Lincoln', 'WA_Spokane', 'WA_Whitman'],
                                                                'NScounties': ['WA_Adams', 'WA_Walla Walla'] },
    {'identifier': 'W7W/WH', 'name': 'WA-Whatcom',                  'counties': ['WA_Whatcom'] },

    # W7I: 12 regions, 44 counties
    # counties not in any region: (none)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W7I/BL', 'name': 'ID - Blaine County',          'counties': ['ID_Blaine'] },
    {'identifier': 'W7I/BC', 'name': 'ID - Boise County',           'counties': ['ID_Boise'] },
    {'identifier': 'W7I/CU', 'name': 'ID - Custer County',          'counties': ['ID_Custer'] },
    {'identifier': 'W7I/ER', 'name': 'ID - Eastern Region',         'counties': ['ID_Clark', 'ID_Fremont', 'ID_Jefferson', 'ID_Madison', 'ID_Teton', 'ID_Bonneville'] },
    {'identifier': 'W7I/IC', 'name': 'ID - Idaho County',           'counties': ['ID_Idaho'] },
    {'identifier': 'W7I/LE', 'name': 'ID - Lemhi County',           'counties': ['ID_Lemhi'] },
    {'identifier': 'W7I/NP', 'name': 'ID - Northern Panhandle',     'counties': ['ID_Bonner', 'ID_Boundary', 'ID_Kootenai'] },
    {'identifier': 'W7I/NI', 'name': 'ID - NorthCentral Idaho',     'counties': ['ID_Benewah', 'ID_Clearwater', 'ID_Latah', 'ID_Nez Perce', 'ID_Shoshone'],
                                                                'NScounties': ['ID_Lewis'] },
    {'identifier': 'W7I/CI', 'name': 'ID - SouthCentral Idaho',     'counties': ['ID_Butte', 'ID_Camas', 'ID_Cassia', 'ID_Minidoka', 'ID_Twin Falls'],
                                                                'NScounties': ['ID_Gooding', 'ID_Jerome', 'ID_Lincoln'] },
    {'identifier': 'W7I/SI', 'name': 'ID - SouthEastern Idaho',     'counties': ['ID_Bear Lake', 'ID_Franklin', 'ID_Bannock', 'ID_Caribou', 'ID_Power', 'ID_Oneida', 'ID_Bingham'] },
    {'identifier': 'W7I/SR', 'name': 'ID - SouthWestern Region',    'counties': ['ID_Elmore', 'ID_Adams', 'ID_Owyhee', 'ID_Washington', 'ID_Gem', 'ID_Ada', 'ID_Payette', 'ID_Canyon'] },
    {'identifier': 'W7I/VC', 'name': 'ID - Valley County',          'counties': ['ID_Valley'] },

    # W7Y: 7 regions, 23 counties
    # counties not in any region: (none)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W7Y/EW', 'name': 'East Wyoming',                'counties': ['WY_Albany', 'WY_Campbell', 'WY_Converse', 'WY_Crook', 'WY_Goshen', 'WY_Niobrara', 'WY_Platte', 'WY_Weston'],
                                                                'NScounties': ['WY_Laramie'] },
    {'identifier': 'W7Y/FT', 'name': 'Fremont',                     'counties': ['WY_Fremont'] },
    {'identifier': 'W7Y/NW', 'name': 'North Wyoming',               'counties': ['WY_Big Horn', 'WY_Sheridan', 'WY_Johnson', 'WY_Hot Springs', 'WY_Washakie', 'WY_Natrona'] },
    {'identifier': 'W7Y/PA', 'name': 'Park',                        'counties': ['WY_Park'] },
    {'identifier': 'W7Y/SL', 'name': 'Sublette',                    'counties': ['WY_Sublette'] },
    {'identifier': 'W7Y/SW', 'name': 'South Wyoming',               'counties': ['WY_Lincoln', 'WY_Uinta', 'WY_Sweetwater', 'WY_Carbon'] },
    {'identifier': 'W7Y/TT', 'name': 'Teton',                       'counties': ['WY_Teton'] },

    # W0N: 2 regions, 93 counties
    # counties not in any region: (64 counties)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W0N/PH', 'name': 'Panhandle',   'counties': ['NE_Sioux', 'NE_Dawes', 'NE_Sheridan', 'NE_Scotts Bluff', 'NE_Banner', 'NE_Morrill'],
                                                'NScounties': ['NE_Box Butte', 'NE_Kimball', 'NE_Cheyenne', 'NE_Garden', 'NE_Deuel'] },
    {'identifier': 'W0N/SH', 'name': 'Sandhills',   'counties': ['NE_Grant'],
                                                'NScounties': ['NE_Cherry', 'NE_Hooker', 'NE_Thomas', 'NE_Keya Paha', 'NE_Brown', 'NE_Rock', 'NE_Boyd', 'NE_Holt', 'NE_Blaine', 'NE_Loup', 'NE_Custer', 'NE_Garfield', 'NE_Wheeler', 'NE_Valley', 'NE_Greeley', 'NE_Sherman', 'NE_Howard'] },

    # W4K: 3 regions, 120 counties
    # counties not in any region: ("Jackson Purchase", "Western Coal Field", and "Bluegrass" regions on map in Association Reference Manual)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W4K/EC', 'name': 'East Coal Field Mountains',   'counties': ['KY_Powell', 'KY_Rowan', 'KY_McCreary', 'KY_Whitley', 'KY_Knox', 'KY_Bell', 'KY_Harlan', 'KY_Clay', 'KY_Leslie', 'KY_Perry', 'KY_Letcher', 'KY_Knott', 'KY_Pike', 'KY_Floyd', 'KY_Martin', 'KY_Johnson', 'KY_Laurel'],
                                                                'NScounties': ['KY_Greenup', 'KY_Boyd', 'KY_Carter', 'KY_Lawrence', 'KY_Elliott', 'KY_Morgan', 'KY_Menifee', 'KY_Montgomery', 'KY_Wolfe', 'KY_Magoffin', 'KY_Lee', 'KY_Breathitt', 'KY_Owsley', 'KY_Jackson'] },
    {'identifier': 'W4K/KA', 'name': 'Knob Arc Mountains',          'counties': ['KY_Bullitt', 'KY_Madison', 'KY_Estill'],
                                                                'NScounties': ['KY_Nelson', 'KY_Marion', 'KY_Lincoln', 'KY_Rockcastle', 'KY_Garrard'] },
    {'identifier': 'W4K/PR', 'name': 'Pennyrile Mountains',         'counties': ['KY_Casey', 'KY_Pulaski', 'KY_Clinton', 'KY_Wayne'],
                                                                'NScounties': ['KY_Livingston', 'KY_Crittenden', 'KY_Lyon', 'KY_Trigg', 'KY_Caldwell', 'KY_Hopkins', 'KY_Christian', 'KY_Todd', 'KY_Logan', 'KY_Simpson', 'KY_Warren', 'KY_Allen', 'KY_Breckinridge', 'KY_Meade', 'KY_Hardin', 'KY_Larue', 'KY_Hart', 'KY_Barren', 'KY_Monroe', 'KY_Cumberland', 'KY_Metcalfe', 'KY_Green', 'KY_Taylor', 'KY_Adair', 'KY_Russell'] },

    # W4A: 4 regions, 67 counties
    # counties not in any region: (53 counties)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W4A/CP', 'name': 'Cumberland Plateau',  'counties': ['AL_DeKalb', 'AL_Marshall', 'AL_Jackson', 'AL_Blount', 'AL_Etowah'] },
    {'identifier': 'W4A/HR', 'name': 'Highland Rim',        'counties': ['AL_Morgan', 'AL_Madison'] },
    {'identifier': 'W4A/PT', 'name': 'Piedmont',            'counties': ['AL_Cleburne', 'AL_Clay'] },
    {'identifier': 'W4A/VR', 'name': 'Valley and Ridge',    'counties': ['AL_Cherokee', 'AL_Shelby', 'AL_Talladega', 'AL_St. Clair', 'AL_Calhoun'] },

    # W4G: 3 regions, 159 counties
    # counties not in any region: (136 counties)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W4G/CE', 'name': 'Central',                 'counties': ['GA_Harris', 'GA_Cobb', 'GA_DeKalb'] },
    {'identifier': 'W4G/HC', 'name': 'Historic High Country',   'counties': ['GA_Floyd', 'GA_Chattooga', 'GA_Dade', 'GA_Walker', 'GA_Gordon', 'GA_Whitfield', 'GA_Bartow', 'GA_Murray', 'GA_Cherokee', 'GA_Pickens', 'GA_Gilmer', 'GA_Fannin'] },
    {'identifier': 'W4G/NG', 'name': 'North Georgia',           'counties': ['GA_Forsyth', 'GA_Stephens', 'GA_Rabun', 'GA_Habersham', 'GA_Towns', 'GA_White', 'GA_Lumpkin', 'GA_Union'] },

    # W4V: 9 regions, 133 "counties" (95 counties + 38 independent cities)
    # counties not in any region: (generally the Eastern portion of the state - flat)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W4V/AB', 'name': 'VA-Abingdon',         'counties': ['VA_Dickenson', 'VA_Buchanan', 'VA_Russell', 'VA_Tazewell', 'VA_Washington'] },
    {'identifier': 'W4V/BR', 'name': 'VA-Blue Ridge',       'counties': ['VA_Amherst', 'VA_Nelson', 'VA_Buckingham', 'VA_Albemarle'],
                                                        'NScounties': ['VA_Appomattox'] },
    {'identifier': 'W4V/FC', 'name': 'VA-Fincastle',        'counties': ['VA_Floyd', 'VA_Montgomery', 'VA_Giles', 'VA_Craig', 'VA_Botetourt'] },
    {'identifier': 'W4V/GC', 'name': 'VA-Gate City',        'counties': ['VA_Lee', 'VA_Wise', 'VA_Scott'] },
    {'identifier': 'W4V/HB', 'name': 'VA-Harrisonburg',     'counties': ['VA_Augusta', 'VA_Rockingham', 'VA_Shenandoah'] },
    {'identifier': 'W4V/LX', 'name': 'VA-Lexington',        'counties': ['VA_Rockbridge', 'VA_Alleghany', 'VA_Bath', 'VA_Highland'] },
    {'identifier': 'W4V/RA', 'name': 'VA-Roanoke',          'counties': ['VA_Patrick', 'VA_Henry', 'VA_Pittsylvania', 'VA_Franklin', 'VA_Roanoke', 'VA_Bedford', 'VA_Campbell'] },
    {'identifier': 'W4V/SH', 'name': 'VA-Shenandoah Park',  'counties': ['VA_Greene', 'VA_Orange', 'VA_Madison', 'VA_Page', 'VA_Rappahannock', 'VA_Fauquier', 'VA_Warren', 'VA_Frederick', 'VA_Loudoun'],
                                                        'NScounties': ['VA_Clarke', 'VA_Culpeper'] },
    {'identifier': 'W4V/WV', 'name': 'VA-Wytheville Park',  'counties': ['VA_Bland', 'VA_Wythe', 'VA_Pulaski', 'VA_Carroll', 'VA_Grayson', 'VA_Smyth'] },

    # W8O: 4 regions, 88 counties
    # counties not in any region: 22 (NW region in map in Association Reference Manual)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W8O/CT', 'name': 'Central',     'counties': ['OH_Logan', 'OH_Licking', 'OH_Fairfield'],
                                                'NScounties': ['OH_Union', 'OH_Marion', 'OH_Morrow', 'OH_Delaware', 'OH_Knox', 'OH_Franklin', 'OH_Madison', 'OH_Pickaway'] },
    {'identifier': 'W8O/NE', 'name': 'Northeast',   'counties': ['OH_Ashland', 'OH_Holmes', 'OH_Tuscarawas', 'OH_Summit', 'OH_Richland', 'OH_Columbiana', 'OH_Geauga', 'OH_Coshocton', 'OH_Jefferson'],
                                                'NScounties': ['OH_Lorain', 'OH_Cuyahoga', 'OH_Medina', 'OH_Wayne', 'OH_Stark', 'OH_Portage', 'OH_Lake', 'OH_Ashtabula', 'OH_Trumbull', 'OH_Mahoning', 'OH_Carroll', 'OH_Harrison'] },
    {'identifier': 'W8O/SE', 'name': 'Southeast',   'counties': ['OH_Muskingum', 'OH_Lawrence', 'OH_Gallia', 'OH_Scioto', 'OH_Pike', 'OH_Vinton', 'OH_Ross'],
                                                'NScounties': ['OH_Jackson', 'OH_Meigs', 'OH_Hocking', 'OH_Athens', 'OH_Perry', 'OH_Morgan', 'OH_Washington', 'OH_Monroe', 'OH_Noble', 'OH_Guernsey', 'OH_Belmont'] },
    {'identifier': 'W8O/SW', 'name': 'Southwest',   'counties': ['OH_Hamilton', 'OH_Highland', 'OH_Adams'],
                                                'NScounties': ['OH_Darke', 'OH_Miami', 'OH_Champaign', 'OH_Clark', 'OH_Greene', 'OH_Montgomery', 'OH_Preble', 'OH_Butler', 'OH_Warren', 'OH_Clinton', 'OH_Fayette', 'OH_Brown', 'OH_Clermont'] },

    # W8V: 8 regions, 55 counties
    # counties not in any region: 7 ("Mid-Ohio Valley" region in map in Association Reference Manual)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W8V/NP', 'name': 'Eastern Panhandle',           'counties': ['WV_Berkeley', 'WV_Morgan', 'WV_Jefferson'] },
    {'identifier': 'W8V/HM', 'name': 'Hatfield-McCoy Mountains',    'counties': ['WV_Wayne', 'WV_Lincoln', 'WV_Logan', 'WV_Boone'] }, # Mingo?
    {'identifier': 'W8V/MC', 'name': 'Mountaineer Country',         'counties': ['WV_Preston', 'WV_Barbour', 'WV_Monongalia', 'WV_Taylor'],
                                                                'NScounties': ['WV_Doddridge', 'WV_Harrison', 'WV_Marion'] },
    {'identifier': 'W8V/ML', 'name': 'Mountain Lakes',              'counties': ['WV_Webster', 'WV_Nicholas', 'WV_Braxton', 'WV_Lewis', 'WV_Clay'],
                                                                'NScounties': ['WV_Gilmer', 'WV_Upshur'] },
    {'identifier': 'W8V/MV', 'name': 'Metro Valley',                'counties': ['WV_Mingo'],
                                                                'NScounties': ['WV_Cabell', 'WV_Mason', 'WV_Putnam', 'WV_Kanawha'] },
    {'identifier': 'W8V/EP', 'name': 'Northern Panhandle',          'counties': ['WV_Tyler'],
                                                                'NScounties': ['WV_Wetzel', 'WV_Marshall', 'WV_Ohio', 'WV_Brooke', 'WV_Hancock'] },
    {'identifier': 'W8V/NR', 'name': 'New River',                   'counties': ['WV_Greenbrier', 'WV_Summers', 'WV_Monroe', 'WV_Raleigh', 'WV_Wyoming', 'WV_Mercer', 'WV_McDowell', 'WV_Fayette'] },
    {'identifier': 'W8V/PH', 'name': 'Potomac Highlands',           'counties': ['WV_Pendleton', 'WV_Pocahontas', 'WV_Randolph', 'WV_Tucker', 'WV_Grant', 'WV_Hardy', 'WV_Mineral', 'WV_Hampshire'] },

    # W4C: 6 regions, 2 states, SC: 46 counties / NC: 100 counties
    # counties not in any region: (SC Midlands/ML, SC LC/Lowcountry, NC CP/Coastalplains regions on map in Association Reference Manual)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W4C/CM', 'name': 'NC-Central Mountains',    'counties': ['NC_Transylvania', 'NC_Haywood', 'NC_Madison', 'NC_Buncombe', 'NC_Henderson', 'NC_Polk', 'NC_Rutherford', 'NC_McDowell', 'NC_Yancey', 'NC_Mitchell'] },
    {'identifier': 'W4C/EM', 'name': 'NC-Eastern Mountains',    'counties': ['NC_Burke', 'NC_Avery', 'NC_Watauga', 'NC_Caldwell', 'NC_Ashe', 'NC_Wilkes', 'NC_Alleghany', 'NC_Surry'] },
    {'identifier': 'W4C/EP', 'name': 'NC-Eastern Piedmont',     'counties': ['NC_Stokes', 'NC_Yadkin', 'NC_Davidson', 'NC_Randolph'],
                                                            'NScounties': ['NC_Forsyth', 'NC_Davie', 'NC_Rockingham', 'NC_Guilford', 'NC_Montgomery', 'NC_Richmond', 'NC_Moore', 'NC_Lee', 'NC_Chatham', 'NC_Alamance', 'NC_Caswell', 'NC_Person', 'NC_Orange', 'NC_Durham', 'NC_Wake', 'NC_Franklin', 'NC_Granville', 'NC_Vance', 'NC_Warren'] },
    {'identifier': 'W4C/US', 'name': 'SC-Upstate',              'counties': ['SC_Oconee', 'SC_Pickens', 'SC_Greenville'],
                                                            'NScounties': ['SC_Anderson', 'SC_Abbeville', 'SC_Laurens', 'SC_Spartanburg', 'SC_Union', 'SC_Cherokee', 'SC_York', 'SC_Chester'] },
    {'identifier': 'W4C/WM', 'name': 'NC-Western Mountains',    'counties': ['NC_Cherokee', 'NC_Graham', 'NC_Clay', 'NC_Macon', 'NC_Swain', 'NC_Jackson'] },
    {'identifier': 'W4C/WP', 'name': 'NC-Western Piedmont',     'counties': ['NC_Catawba', 'NC_Alexander', 'NC_Gaston'],
                                                            'NScounties': ['NC_Cleveland', 'NC_Lincoln', 'NC_Iredell', 'NC_Rowan', 'NC_Mecklenburg', 'NC_Union', 'NC_Anson', 'NC_Stanly', 'NC_Cabarrus'] },

    # W3: 10 regions, 3 states, DE: 3 counties / MD: 24 "counties" (23 counties + 1 independent city) / PA: 67 counties
    # counties not in any region: (all of Delaware, others?)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W3/CR', 'name': 'Capital Region',      'counties': ['MD_Frederick', 'MD_Montgomery'],
                                                        'NScounties': ["MD_Prince George's"] },
    {'identifier': 'W3/WE', 'name': 'Western',             'counties': ['MD_Allegany', 'MD_Washington', 'MD_Garrett'] },
    {'identifier': 'W3/CT', 'name': 'Central Ranges',      'counties': ['MD_Carroll'] }, # no summits: others? region is missing from ARM
    # Eastern Shore ES- and Southern SO- regions have 0 summits

    {'identifier': 'W3/PD', 'name': 'Pennsylvania Dutch',  'counties': ['PA_Franklin', 'PA_Perry', 'PA_Cumberland', 'PA_Adams', 'PA_Dauphin', 'PA_Lebanon', 'PA_York', 'PA_Lancaster'] },
    {'identifier': 'W3/ER', 'name': 'Erie',                'counties': ['PA_Mercer'],
                                                        'NScounties': ['PA_Erie', 'PA_Crawford', 'PA_Venango'] },
    {'identifier': 'W3/PH', 'name': 'Philadelphia',        'counties': ['PA_Northampton', 'PA_Berks', 'PA_Lehigh'],
                                                        'NScounties': ['PA_Bucks', 'PA_Chester', 'PA_Montgomery'] },
    {'identifier': 'W3/PO', 'name': 'Pocono',              'counties': ['PA_Carbon', 'PA_Monroe', 'PA_Luzerne', 'PA_Wyoming', 'PA_Lackawanna', 'PA_Sullivan', 'PA_Bradford', 'PA_Susquehanna', 'PA_Wayne'],
                                                        'NScounties': ['PA_Pike'] },
    {'identifier': 'W3/PT', 'name': 'Pittsburgh',          'counties': ['PA_Fayette', 'PA_Somerset', 'PA_Westmoreland', 'PA_Indiana'] }, # no summits: 7 more?
    {'identifier': 'W3/PW', 'name': 'Pennsylvania Wilds',  'counties': ['PA_Warren', 'PA_Jefferson', 'PA_McKean', 'PA_Potter', 'PA_Cameron', 'PA_Tioga', 'PA_Lycoming', 'PA_Clinton', 'PA_Centre', 'PA_Clearfield'] }, # no summits: 3 more?
    {'identifier': 'W3/SV', 'name': 'Susquehanna Valley',  'counties': ['PA_Cambria', 'PA_Bedford', 'PA_Blair', 'PA_Fulton', 'PA_Huntingdon', 'PA_Mifflin', 'PA_Juniata', 'PA_Snyder', 'PA_Union', 'PA_Northumberland', 'PA_Columbia', 'PA_Schuylkill'] }, # no summits: Montour?

    # W9: 3 regions, 3 states, WI: 72 counties / IL: 102 counties / IN: 92 counties
    # counties not in any region: (?)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W9/IL', 'name': 'Illinois',    'type': 'state', 'state': 'IL' },
    {'identifier': 'W9/IN', 'name': 'Indiana',     'type': 'state', 'state': 'IN' },
    {'identifier': 'W9/WI', 'name': 'Wisconsin',   'type': 'state', 'state': 'WI' },
    # {'identifier': 'IL', 'name': 'Illinois',    'counties': ['Jackson', 'Union', 'Gallatin', 'Pope', 'Saline'] }, # no summits: (97 counties)
    # {'identifier': 'IN', 'name': 'Indiana',     'counties': ['Washington', 'Jackson', 'Harrison'] }, # no summits: (89 counties)
    # {'identifier': 'WI', 'name': 'Wisconsin',   'counties': [''] }, # just do all of WI?

    # K0M: 3 regions, 87 counties
    # counties not in any region: (79 counties)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'K0M/CW', 'name': 'Centralwest', 'counties': ['MN_Clearwater', 'MN_Otter Tail'] },
    {'identifier': 'K0M/NE', 'name': 'Northeast',   'counties': ['MN_Cook', 'MN_Lake', 'MN_St. Louis', 'MN_Itasca'] },
    {'identifier': 'K0M/SE', 'name': 'Southeast',   'counties': ['MN_Houston', 'MN_Goodhue'] },

    # W0D: 5 regions, 2 states, ND: 53 counties / SD: 66 counties
    # counties not in any region: (47 counties in South Dakota)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W0D/BB', 'name': 'SD-Black Hills - Badlands',   'counties': ['SD_Pennington', 'SD_Custer', 'SD_Fall River', 'SD_Jackson', 'SD_Bennett', 'SD_Oglala Lakota'] }, # Oglala Lakota is referred to as Shannon county in the ARM (changed 2015)
    {'identifier': 'W0D/ES', 'name': 'Eastern South Dakota',        'counties': ['SD_Hyde', 'SD_Roberts'] },
    {'identifier': 'W0D/MR', 'name': 'Missouri River',              'counties': ['SD_Tripp', 'SD_Lyman', 'SD_Walworth', 'SD_Gregory', 'SD_Campbell', 'SD_Charles Mix', 'SD_Bon Homme'] },
    {'identifier': 'W0D/NW', 'name': 'Custer Region',               'counties': ['SD_Lawrence', 'SD_Meade', 'SD_Harding', 'SD_Butte'] },
    # {'identifier': 'ND', 'name': 'North Dakota',                'counties': ['Golden Valley', 'Billings', 'Slope', 'Bowman', 'Dunn', 'Stark', 'Hettinger', 'Grant', 'McKenzie', 'Mountrail', 'Sioux', 'Bottineau', 'Morton', 'Kidder', 'Williams', 'Logan', 'Emmons', 'Burleigh'] }, # no summits: (other 35 counties in ND)
    {'identifier': 'W0D/ND', 'name': 'North Dakota',    'type': 'state', 'state': 'ND' },

    # W0M: 3 regions, 115 counties
    # counties not in any region: (104 counties)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W0M/ES', 'name': 'Eureka Springs Escarpment',   'counties': ['MO_Webster', 'MO_Ozark', 'MO_Stone'] },
    {'identifier': 'W0M/SF', 'name': 'Saint Francois Mountains',    'counties': ['MO_Iron', 'MO_Reynolds', 'MO_St. Francois', 'MO_Madison', 'MO_Wayne', 'MO_Washington', 'MO_Ste. Genevieve'] },
    {'identifier': 'W0M/SP', 'name': 'Salem Plateau',               'counties': ['MO_Shannon'] },

    # W2: 5 regions, 2 states, NY: 62 counties / NJ: 21 counties
    # counties not in any region: (some in NY and NJ)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W2/EH', 'name': 'East of the Hudson',  'counties': ['NY_Putnam', 'NY_Dutchess', 'NY_Columbia', 'NY_Rensselaer'] },
    {'identifier': 'W2/GA', 'name': 'Greater Adirondacks', 'counties': ['NY_Lewis', 'NY_Oneida', 'NY_Herkimer', 'NY_St. Lawrence', 'NY_Hamilton', 'NY_Franklin', 'NY_Clinton', 'NY_Essex', 'NY_Warren', 'NY_Fulton', 'NY_Saratoga', 'NY_Washington'] },
    {'identifier': 'W2/GC', 'name': 'Greater Catskills',   'counties': ['NY_Schenectady', 'NY_Schoharie', 'NY_Otsego', 'NY_Delaware', 'NY_Sullivan', 'NY_Ulster', 'NY_Greene', 'NY_Orange', 'NY_Rockland'] }, # no summits: Albany
    # {'identifier': 'NJ', 'name': 'New Jersey',          'counties': ['Hunterdon', 'Warren', 'Sussex', 'Passaic', 'Bergen'] }, # no summits: 16 more?
    {'identifier': 'W2/NJ', 'name': 'New Jersey',  'type': 'state', 'state': 'NJ' },
    {'identifier': 'W2/WE', 'name': 'Western New York',    'counties': ['NY_Chautauqua', 'NY_Cattaraugus', 'NY_Erie', 'NY_Allegany', 'NY_Livingston', 'NY_Steuben', 'NY_Ontario', 'NY_Yates', 'NY_Schuyler', 'NY_Chemung', 'NY_Tompkins', 'NY_Tioga', 'NY_Cayuga', 'NY_Cortland', 'NY_Onondaga', 'NY_Madison', 'NY_Chenango', 'NY_Broome'] },

    # W0I: 1 region, 99 counties
    # counties not in any region: (97 counties)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W0I/IA', 'name': 'Iowa',    'type': 'state', 'state': 'IA' },
    # {'identifier': 'IA', 'name': 'Iowa',    'counties': ['Carroll', 'Hancock'] },

    # W5M: 1 region, 82 counties
    # counties not in any region: (81 counties)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W5M/MS', 'name': 'Mississippi Mountains',   'type': 'state', 'state': 'MS' },
    # {'identifier': 'MS', 'name': 'Mississippi Mountains',   'counties': ['Choctaw'] },

    # W8M: 2 regions, 83 counties
    # counties not in any region: (?)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W8M/LP', 'name': 'Michigan Lower Peninsula',    'counties': ['MI_Alcona', 'MI_Allegan', 'MI_Alpena', 'MI_Antrim', 'MI_Arenac', 'MI_Barry', 'MI_Bay', 'MI_Benzie', 'MI_Berrien', 'MI_Branch', 'MI_Calhoun', 'MI_Cass', 'MI_Charlevoix', 'MI_Cheboygan', 'MI_Clare', 'MI_Clinton', 'MI_Crawford', 'MI_Eaton', 'MI_Emmet', 'MI_Genesee', 'MI_Gladwin', 'MI_Grand Traverse', 'MI_Gratiot', 'MI_Hillsdale', 'MI_Huron', 'MI_Ingham', 'MI_Ionia', 'MI_Iosco', 'MI_Isabella', 'MI_Jackson', 'MI_Kalamazoo', 'MI_Kalkaska', 'MI_Kent', 'MI_Lake', 'MI_Lapeer', 'MI_Leelanau', 'MI_Lenawee', 'MI_Livingston', 'MI_Macomb', 'MI_Manistee', 'MI_Mason', 'MI_Mecosta', 'MI_Midland', 'MI_Missaukee', 'MI_Monroe', 'MI_Montcalm', 'MI_Montmorency', 'MI_Muskegon', 'MI_Newaygo', 'MI_Oakland', 'MI_Oceana', 'MI_Ogemaw', 'MI_Osceola', 'MI_Oscoda', 'MI_Otsego', 'MI_Ottawa', 'MI_Presque Isle', 'MI_Roscommon', 'MI_Saginaw', 'MI_St. Clair', 'MI_St. Joseph', 'MI_Sanilac', 'MI_Shiawassee', 'MI_Tuscola', 'MI_Van Buren', 'MI_Washtenaw', 'MI_Wayne', 'MI_Wexford'] },
    {'identifier': 'W8M/UP', 'name': 'Michigan Upper Peninsula',    'counties': ['MI_Keweenaw', 'MI_Ontonagon', 'MI_Luce', 'MI_Schoolcraft', 'MI_Baraga', 'MI_Alger', 'MI_Iron', 'MI_Mackinac', 'MI_Gogebic', 'MI_Menominee', 'MI_Chippewa', 'MI_Delta', 'MI_Dickinson', 'MI_Marquette', 'MI_Houghton'] },

    # W5A: 8 regions, 75 counties
    # counties not in any region: (?)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W5A/BR', 'name': 'Buffalo River',       'type': 'concave-hull' },
    {'identifier': 'W5A/CA', 'name': 'Caddo Mountains',     'type': 'concave-hull' },
    {'identifier': 'W5A/CS', 'name': 'Cossatot Mountains',  'type': 'concave-hull' },
    {'identifier': 'W5A/MA', 'name': 'Magazine Mountains',  'type': 'concave-hull' },
    {'identifier': 'W5A/OA', 'name': 'Oak Mountains',       'type': 'concave-hull' },
    {'identifier': 'W5A/OH', 'name': 'Ouachita Mountains',  'type': 'concave-hull' },
    {'identifier': 'W5A/OZ', 'name': 'Ozark Mountains',     'type': 'concave-hull' },
    {'identifier': 'W5A/PT', 'name': 'Poteau Mountains',    'type': 'concave-hull' },

    # W5N: 37 regions, 33 counties
    # counties not in any region: (?)
    # regions overlaying other regions: (none)
    # split counties (21): Grant, Hidalgo, Catron, Sierra, Cibola, Socorro, McKinley, Mora, Torrance, Luna, Lincoln, Otero, Rio Arriba, Taos, San Miguel, Doña Ana, Santa Fe, Sandoval, Colfax, Union, Valencia
    {'identifier': 'W5N/AI', 'name': 'Animas Mountains',                'type': 'concave-hull' }, # 'counties': ['Hidalgo'] },
    {'identifier': 'W5N/AP', 'name': 'Apache National Forest',          'type': 'concave-hull' }, # 'counties': ['Catron', 'Cibola'] },
    {'identifier': 'W5N/BA', 'name': 'Bosque Del Apache NWR',           'type': 'concave-hull' }, # 'counties': ['Socorro', 'Torrance'] },
    {'identifier': 'W5N/BL', 'name': 'Black Range',                     'type': 'concave-hull' }, # 'counties': ['Grant', 'Sierra'] },
    {'identifier': 'W5N/BU', 'name': 'Burro Mountains',                 'type': 'concave-hull' }, # 'counties': ['Grant', 'Hidalgo', 'Catron', 'Luna'] },
    {'identifier': 'W5N/CB', 'name': 'Caballo Mountains',               'type': 'concave-hull' }, # 'counties': ['Sierra'] },
    {'identifier': 'W5N/CC', 'name': 'Chama Canyon',                    'type': 'concave-hull' }, # 'counties': ['Rio Arriba'] },
    {'identifier': 'W5N/CD', 'name': 'Coronado National Forest',        'type': 'concave-hull' }, # 'counties': ['Hidalgo'] },
    {'identifier': 'W5N/CM', 'name': 'Cimarron Range',                  'type': 'concave-hull' }, # 'counties': ['Colfax', 'Taos', 'Mora'] },
    {'identifier': 'W5N/CN', 'name': 'Cornudas Mountains',              'type': 'concave-hull' }, # 'counties': ['Eddy', 'Otero'] },
    {'identifier': 'W5N/CO', 'name': 'Cibola National Forest',          'type': 'concave-hull' }, # 'counties': ['Cibola', 'McKinley', 'Socorro', 'Catron'] },
    {'identifier': 'W5N/CU', 'name': 'Chuska Mountains',                'type': 'concave-hull' }, # 'counties': ['San Juan', 'McKinley'] },
    {'identifier': 'W5N/DA', 'name': 'Datil Mountains',                 'type': 'concave-hull' }, # 'counties': ['Catron', 'Socorro'] },
    {'identifier': 'W5N/EL', 'name': 'Eastern New Mexico Flatlands',    'type': 'concave-hull' }, # 'counties': ['Lincoln', 'Mora', 'Torrance', 'San Miguel', 'Union', 'Guadalupe', 'Quay', 'Harding'] },
    {'identifier': 'W5N/FL', 'name': 'Florida Mountains',               'type': 'concave-hull' }, # 'counties': ['Luna'] },
    {'identifier': 'W5N/GF', 'name': 'Gila National Forest',            'type': 'concave-hull' }, # 'counties': ['Catron', 'Sierra'] },
    {'identifier': 'W5N/GW', 'name': 'Gila Wilderness',                 'type': 'concave-hull' }, # 'counties': ['Catron', 'Grant'] },
    {'identifier': 'W5N/HT', 'name': 'Hatchet Mountains',               'type': 'concave-hull' }, # 'counties': ['Hidalgo', 'Luna', 'Grant'] },
    {'identifier': 'W5N/MG', 'name': 'Magdalena Mountains',             'type': 'concave-hull' }, # 'counties': ['Socorro', 'Sierra'] },
    {'identifier': 'W5N/MI', 'name': 'Mimbres Mountains',               'type': 'concave-hull' }, # 'counties': ['Grant', 'Luna', 'Sierra'] },
    {'identifier': 'W5N/MO', 'name': 'Mockingbird Mountains',           'type': 'concave-hull' }, # 'counties': ['Sierra', 'Lincoln', 'Socorro'] },
    {'identifier': 'W5N/NL', 'name': 'Navajo Lake',                     'type': 'concave-hull' }, # 'counties': ['San Juan'] },
    {'identifier': 'W5N/OR', 'name': 'Organ Mountains',                 'type': 'concave-hull' }, # 'counties': ['Doña Ana', 'Otero'] },
    {'identifier': 'W5N/OT', 'name': 'Ortega Mountains',                'type': 'concave-hull' }, # 'counties': ['Rio Arriba', 'Taos'] },
    {'identifier': 'W5N/PA', 'name': 'Pinos Altos Range',               'type': 'concave-hull' }, # 'counties': ['Grant', 'Luna'] },
    {'identifier': 'W5N/PL', 'name': 'Peloncillo Mountains',            'type': 'concave-hull' }, # 'counties': ['Hidalgo'] },
    {'identifier': 'W5N/PO', 'name': 'Potrillo Mountains',              'type': 'concave-hull' }, # 'counties': ['Doña Ana', 'Luna'] },
    {'identifier': 'W5N/PW', 'name': 'Pecos Wilderness',                'type': 'concave-hull' }, # 'counties': ['Mora', 'Rio Arriba', 'Taos', 'Santa Fe', 'San Miguel'] },
    {'identifier': 'W5N/RO', 'name': 'Robledo Mountains',               'type': 'concave-hull' }, # 'counties': ['Doña Ana', 'Luna'] },
    {'identifier': 'W5N/SC', 'name': 'Sacramento Mountains',            'type': 'concave-hull' }, # 'counties': ['Otero', 'Lincoln', 'Chaves'] },
    {'identifier': 'W5N/SE', 'name': 'Sierra De Las Valles Range',      'type': 'concave-hull' }, # 'counties': ['Rio Arriba', 'Sandoval', 'Santa Fe'] },
    {'identifier': 'W5N/SG', 'name': 'Sierra Grande Range',             'type': 'concave-hull' }, # 'counties': ['Colfax', 'Union'] },
    {'identifier': 'W5N/SI', 'name': 'Sandia Mountains',                'type': 'concave-hull' }, # 'counties': ['Bernalillo', 'Torrance', 'Santa Fe', 'Sandoval', 'Valencia'] },
    {'identifier': 'W5N/SL', 'name': 'Sierra Lucero Range',             'type': 'concave-hull' }, # 'counties': ['Cibola', 'Socorro', 'Valencia'] },
    {'identifier': 'W5N/SM', 'name': 'San Mateo Mountains',             'type': 'concave-hull' }, # 'counties': ['Cibola', 'McKinley', 'Sandoval'] },
    {'identifier': 'W5N/SR', 'name': 'San Andres Mountains',            'type': 'concave-hull' }, # 'counties': ['Doña Ana', 'Sierra'] },
    {'identifier': 'W5N/SS', 'name': 'Sangre De Cristo Mountains',      'type': 'concave-hull' }, # 'counties': ['Taos', 'Mora', 'Colfax', 'Rio Arriba'] },

    # W5O: 7 regions, 77 counties
    # counties not in any region: (?)
    # regions overlaying other regions: (none)
    # split counties: (many)
    {'identifier': 'W5O/BS', 'name': 'Brushy Mountains',            'type': 'concave-hull' },
    {'identifier': 'W5O/KI', 'name': 'Kiamichi Mountains',          'type': 'concave-hull' },
    {'identifier': 'W5O/OU', 'name': 'Ouachita National Forest',    'type': 'concave-hull' },
    {'identifier': 'W5O/QA', 'name': 'Quartz Mountains SP',         'type': 'concave-hull' },
    {'identifier': 'W5O/SO', 'name': 'Sans Bois Mountains',         'type': 'concave-hull' },
    {'identifier': 'W5O/WI', 'name': 'Wichita Mountains',           'type': 'concave-hull' },
    {'identifier': 'W5O/WO', 'name': 'White Oak Mountains',         'type': 'concave-hull' },

    # W5T: 26 regions, 254 counties
    # counties not in any region: (?)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W5T/BG', 'name': 'Bullis Gap Mountains',    'type': 'concave-hull' },
    {'identifier': 'W5T/BO', 'name': 'Bofecillos Mountains',    'type': 'concave-hull' },
    {'identifier': 'W5T/CE', 'name': 'Cienega Mountains',       'type': 'concave-hull' },
    {'identifier': 'W5T/CH', 'name': 'Chinati Mountains',       'type': 'concave-hull' },
    {'identifier': 'W5T/CI', 'name': 'Chisos Mountains',        'type': 'concave-hull' },
    {'identifier': 'W5T/CR', 'name': 'Christmas Mountains',     'type': 'concave-hull' },
    {'identifier': 'W5T/DE', 'name': 'Davis Mountains East',    'type': 'concave-hull' },
    {'identifier': 'W5T/DH', 'name': 'Dead Horse Mountains',    'type': 'concave-hull' },
    {'identifier': 'W5T/DN', 'name': 'Del Norte Mountains',     'type': 'concave-hull' },
    {'identifier': 'W5T/DW', 'name': 'Davis Mountains West',    'type': 'concave-hull' },
    {'identifier': 'W5T/EA', 'name': 'Eagle Mountains',         'type': 'concave-hull' },
    {'identifier': 'W5T/EF', 'name': 'Eastern Texas Flatlands', 'type': 'concave-hull' },
    {'identifier': 'W5T/FR', 'name': 'Franklin Mountains',      'type': 'concave-hull' },
    {'identifier': 'W5T/GL', 'name': 'Glass Mountains',         'type': 'concave-hull' },
    {'identifier': 'W5T/GU', 'name': 'Guadalupe Mountains',     'type': 'concave-hull' },
    {'identifier': 'W5T/HA', 'name': 'Haymond Mountains',       'type': 'concave-hull' },
    {'identifier': 'W5T/PB', 'name': 'Pena Blanca Mountains',   'type': 'concave-hull' },
    {'identifier': 'W5T/PU', 'name': 'Puertecita Mountains',    'type': 'concave-hull' },
    {'identifier': 'W5T/QU', 'name': 'Quitman Mountains',       'type': 'concave-hull' },
    {'identifier': 'W5T/SB', 'name': 'Study Butte',             'type': 'concave-hull' },
    {'identifier': 'W5T/SD', 'name': 'Sierra Diablo Mountains', 'type': 'concave-hull' },
    {'identifier': 'W5T/SN', 'name': 'Santiago Mountains',      'type': 'concave-hull' },
    {'identifier': 'W5T/SV', 'name': 'Sierra Vieja Mountains',  'type': 'concave-hull' },
    {'identifier': 'W5T/VH', 'name': 'Van Horn Mountains',      'type': 'concave-hull' },

    {'identifier': 'W5T/NT', 'name': 'North Texas',             'counties': ['TX_Crockett', 'TX_Val Verde', 'TX_Upton', 'TX_Armstrong', 'TX_Newton', 'TX_Stonewall', 'TX_Kent', 'TX_Scurry', 'TX_Young', 'TX_Palo Pinto', 'TX_Callahan', 'TX_Taylor', 'TX_Runnels', 'TX_Coke', 'TX_Llano', 'TX_Blanco', 'TX_Reeves'] },
    {'identifier': 'W5T/ST', 'name': 'South Texas',             'counties': ['TX_Webb', 'TX_Kinney', 'TX_Edwards', 'TX_Real', 'TX_Bandera', 'TX_Uvalde', 'TX_Medina'] },

    # W1: 13 regions, 5 states, CT: 8 counties / MA: 14 counties / VT: 14 counties / NH: 10 counties / ME: 16 counties
    # counties not in any region: (VT: Grand Isle, others: ?)
    # regions overlaying other regions: (none)
    # split counties: Penobscot, Aroostook, Hancock,      Carroll, Grafton, Belknap, Merrimack, Rockingham      Orleans, Caledonia, Essex      Hampden, Franklin     Capitol
    # # Maine
    # {'identifier': 'AM', 'name': 'Appalachian Mountains',       'counties': ['York', 'Oxford', 'Cumberland', 'Androscoggin', 'Franklin', 'Somerset', 'Kennebec', 'Penobscot', 'Piscataquis', 'Aroostook'] },
    # {'identifier': 'EM', 'name': 'Eastern Maine',               'counties': ['Knox', 'Waldo', 'Penobscot', 'Hancock', 'Washington', 'Aroostook'] },
    # {'identifier': 'DI', 'name': 'Desert Island',               'counties': ['Hancock'] },
    # # New Hampshire
    # {'identifier': 'HA', 'name': 'New Hampshire Appalachians',  'counties': ['Cheshire', 'Hillsborough', 'Sullivan', 'Merrimack', 'Grafton', 'Belknap', 'Carroll', 'Coos'] },
    # {'identifier': 'NL', 'name': 'New Hampshire Lakes',         'counties': ['Carroll', 'Grafton', 'Belknap', 'Merrimack', 'Rockingham', 'Strafford'] },
    # {'identifier': 'MV', 'name': 'Merrimack Valley',            'counties': ['Merrimack', 'Hillsborough', 'Rockingham'] },
    # # Vermont
    # {'identifier': 'GM', 'name': 'Green Mountains',             'counties': ['Bennington', 'Windham', 'Windsor', 'Rutland', 'Addison', 'Orange', 'Washington', 'Caledonia', 'Chittenden', 'Lamoille', 'Franklin', 'Orleans', 'Essex'] },
    # {'identifier': 'NK', 'name': 'Northeast Kingdom',           'counties': ['Orleans', 'Caledonia', 'Essex'] },
    # # Massachusetts
    # {'identifier': 'MB', 'name': 'Massachusetts Berkshires',    'counties': ['Berkshire', 'Franklin', 'Hampden'] },
    # {'identifier': 'CR', 'name': 'Connecticut River',           'counties': ['Hampden', 'Hampshire', 'Franklin', 'Worcester'] },
    # # Connecticut
    # {'identifier': 'CB', 'name': 'Connecticut Berkshires',      'counties': ['Northwest Hills', 'Western Connecticut'] },
    # {'identifier': 'MR', 'name': 'Metacomet Ridge',             'counties': ['Capitol'] },
    # {'identifier': 'HH', 'name': 'Hanging Hills',               'counties': ['Capitol', 'South Central Connecticut', 'Lower Connecticut River Valley'] },
    # Maine
    {'identifier': 'W1/AM', 'name': 'Appalachian Mountains',        'type': 'concave-hull' },
    {'identifier': 'W1/EM', 'name': 'Eastern Maine',                'type': 'concave-hull' },
    {'identifier': 'W1/DI', 'name': 'Desert Island',                'type': 'concave-hull' },
    # New Hampshire
    {'identifier': 'W1/HA', 'name': 'New Hampshire Appalachians',   'type': 'concave-hull' },
    {'identifier': 'W1/NL', 'name': 'New Hampshire Lakes',          'type': 'concave-hull' },
    {'identifier': 'W1/MV', 'name': 'Merrimack Valley',             'type': 'concave-hull' },
    # Vermont
    {'identifier': 'W1/GM', 'name': 'Green Mountains', 'type': 'state', 'state': 'VT' },
    {'identifier': 'W1/NK', 'name': 'Northeast Kingdom',            'type': 'concave-hull' },
    # Massachusetts
    {'identifier': 'W1/MB', 'name': 'Massachusetts Berkshires',     'type': 'concave-hull' },
    {'identifier': 'W1/CR', 'name': 'Connecticut River',            'type': 'concave-hull' },
    # Connecticut
    {'identifier': 'W1/CB', 'name': 'Connecticut Berkshires',       'type': 'concave-hull' },
    {'identifier': 'W1/MR', 'name': 'Metacomet Ridge',              'type': 'concave-hull' },
    {'identifier': 'W1/HH', 'name': 'Hanging Hills',                'type': 'concave-hull' },

    # W7O: 10 regions, 36 counties
    # counties not in any region: ?
    # regions overlaying other regions: ?
    # split counties: (many)
    {'identifier': 'W7O/CC', 'name': 'OR-Central Coast',        'type': 'concave-hull' },
    {'identifier': 'W7O/CE', 'name': 'OR-Central Oregon',       'type': 'concave-hull' },
    {'identifier': 'W7O/CM', 'name': 'OR-Cascades Middle',      'type': 'concave-hull' },
    {'identifier': 'W7O/CN', 'name': 'OR-Cascades North',       'type': 'concave-hull' },
    {'identifier': 'W7O/CS', 'name': 'OR-Cascades South',       'type': 'concave-hull' },
    {'identifier': 'W7O/NC', 'name': 'OR-North Coastal',        'type': 'concave-hull' },
    {'identifier': 'W7O/NE', 'name': 'OR-Northeast',            'type': 'concave-hull' },
    {'identifier': 'W7O/SC', 'name': 'OR-South Coastal',        'type': 'concave-hull' },
    {'identifier': 'W7O/SE', 'name': 'OR-Southeast',            'type': 'concave-hull' },
    {'identifier': 'W7O/WV', 'name': 'OR-Willamette Valley',    'type': 'concave-hull' },

    # W0C: 14 regions, 64 counties
    # counties not in any region: (none)
    # regions overlaying other regions: (none)
    # split counties: (none)
    {'identifier': 'W0C/FR', 'name': 'CO-Front Range',          'type': 'concave-hull' },
    {'identifier': 'W0C/LG', 'name': 'CO-La Garita',            'type': 'concave-hull' },
    {'identifier': 'W0C/MZ', 'name': 'CO-Mt Zirkel WA',         'type': 'concave-hull' },
    {'identifier': 'W0C/PR', 'name': 'CO-Park Range',           'type': 'concave-hull' },
    {'identifier': 'W0C/RG', 'name': 'CO-Rio Grande',           'type': 'concave-hull' },
    {'identifier': 'W0C/RP', 'name': 'CO-Roan Plateau',         'type': 'concave-hull' },
    {'identifier': 'W0C/SC', 'name': 'CO-Sangre De Christo',    'type': 'concave-hull' },
    {'identifier': 'W0C/SJ', 'name': 'CO-San Juan',             'type': 'concave-hull' },
    {'identifier': 'W0C/SL', 'name': 'CO-San Luis',             'type': 'concave-hull' },
    {'identifier': 'W0C/SM', 'name': 'CO-San Miguel',           'type': 'concave-hull' },
    {'identifier': 'W0C/SP', 'name': 'CO-South Park',           'type': 'concave-hull' },
    {'identifier': 'W0C/SR', 'name': 'CO-Sawatch Range',        'type': 'concave-hull' },
    {'identifier': 'W0C/UR', 'name': 'CO-Uncompahgre',          'type': 'concave-hull' },
    {'identifier': 'W0C/WE', 'name': 'CO-West Elk Mtns',        'type': 'concave-hull' },

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

    # W7M: 16 regions, 56 counties
    # counties not in any region: (none)
    # regions overlaying other regions: (none)
    # split counties: Flathead
    {'identifier': 'W7M/BE', 'name': 'MT - Beaverhead County',      'counties': ['MT_Beaverhead'] },
    {'identifier': 'W7M/BR', 'name': 'MT - Butte Region',           'counties': ['MT_Madison', 'MT_Deer Lodge', 'MT_Silver Bow'] },
    {'identifier': 'W7M/CL', 'name': 'MT - Lewis & Clark County',   'counties': ['MT_Lewis and Clark'] },
    {'identifier': 'W7M/FN', 'name': 'MT - North Flathead County',  'counties': ['MT_Flathead'], 'linesplit': [[(-179, 48.25), (179, 48.25)], 'N'] },
    {'identifier': 'W7M/FS', 'name': 'MT - South Flathead County',  'counties': ['MT_Flathead'], 'linesplit': [[(-179, 48.25), (179, 48.25)], 'S'] },
    {'identifier': 'W7M/GA', 'name': 'MT - Granite',                'counties': ['MT_Granite', 'MT_Powell'] },
    {'identifier': 'W7M/GR', 'name': 'MT - Glacier Region',         'counties': ['MT_Glacier', 'MT_Teton', 'MT_Pondera'] },
    {'identifier': 'W7M/HB', 'name': 'MT - Helena-Bozeman',         'counties': ['MT_Gallatin', 'MT_Broadwater', 'MT_Jefferson'] },
    {'identifier': 'W7M/LI', 'name': 'MT - Lincoln County',         'counties': ['MT_Lincoln'] },
    {'identifier': 'W7M/LM', 'name': 'MT - Lake-Missoula',          'counties': ['MT_Lake', 'MT_Missoula'] },
    {'identifier': 'W7M/LO', 'name': 'MT - Lolo Region',            'counties': ['MT_Sanders', 'MT_Mineral'] },
    {'identifier': 'W7M/NF', 'name': 'MT - North Central Foothills','counties': ['MT_Cascade', 'MT_Judith Basin', 'MT_Chouteau', 'MT_Toole', 'MT_Liberty', 'MT_Hill'] },
    {'identifier': 'W7M/PN', 'name': 'MT - Northeast Plains',       'counties': ['MT_Fergus', 'MT_Blaine', 'MT_Phillips', 'MT_Garfield', 'MT_Prairie', 'MT_Valley', 'MT_Roosevelt'],
                                                                'NScounties': ['MT_Daniels', 'MT_Dawson', 'MT_McCone', 'MT_Petroleum', 'MT_Richland', 'MT_Sheridan', 'MT_Wibaux'] },
    {'identifier': 'W7M/PS', 'name': 'MT - Southeast Plains',       'counties': ['MT_Stillwater', 'MT_Carbon', 'MT_Big Horn', 'MT_Yellowstone', 'MT_Rosebud', 'MT_Carter', 'MT_Powder River'],
                                                                'NScounties': ['MT_Custer', 'MT_Fallon', 'MT_Golden Valley', 'MT_Musselshell', 'MT_Treasure'] },
    {'identifier': 'W7M/RC', 'name': 'MT - Ravalli County',         'counties': ['MT_Ravalli'] },
    {'identifier': 'W7M/SF', 'name': 'MT - South Central Foothills','counties': ['MT_Park', 'MT_Sweet Grass', 'MT_Meagher', 'MT_Wheatland'] },

    # W7N: 13 regions, 17 counties (all with summits)
    # counties not in any region: (none)
    # regions overlaying other regions: (none)
    # split counties: Elko, Nye
    {'identifier': 'W7N/CK', 'name': 'NV-Clark',                    'counties': ['NV_Clark'] },
    {'identifier': 'W7N/EL', 'name': 'NV-Eureka-Lander',            'counties': ['NV_Eureka', 'NV_Lander'] },
    {'identifier': 'W7N/EM', 'name': 'NV-Esme-Mineral',             'counties': ['NV_Esmeralda', 'NV_Mineral'] },
    {'identifier': 'W7N/EN', 'name': 'NV-Elko North',               'counties': ['NV_Elko'], 'linesplit': [[(-179, 41), (179, 41)], 'N'] },
    {'identifier': 'W7N/ES', 'name': 'NV-Elko South',               'counties': ['NV_Elko'], 'linesplit': [[(-179, 41), (179, 41)], 'S'] },
    {'identifier': 'W7N/HU', 'name': 'NV-Humboldt',                 'counties': ['NV_Humboldt'] },
    {'identifier': 'W7N/LN', 'name': 'NV-Lincoln',                  'counties': ['NV_Lincoln'] },
    {'identifier': 'W7N/NN', 'name': 'NV-Nye North',                'counties': ['NV_Nye'], 'linesplit': [[(-179, 38.25), (179, 38.25)], 'N'] },
    {'identifier': 'W7N/NS', 'name': 'NV-Nye South',                'counties': ['NV_Nye'], 'linesplit': [[(-179, 38.25), (179, 38.25)], 'S'] },
    {'identifier': 'W7N/PC', 'name': 'NV-Pershing-Churchill',       'counties': ['NV_Pershing', 'NV_Churchill'] },
    {'identifier': 'W7N/TR', 'name': 'NV-Tahoe Region',             'counties': ['NV_Carson City', 'NV_Storey', 'NV_Lyon', 'NV_Douglas'] },
    {'identifier': 'W7N/WC', 'name': 'NV-Washoe County',            'counties': ['NV_Washoe'] },
    {'identifier': 'W7N/WP', 'name': 'NV-White Pine',               'counties': ['NV_White Pine'] },

    # W7U: 31 regions, 29 counties (all with summits)
    # tl;dr: polygons should be 1 for each county, then 1 for all of Utah above 39.5°N, then 1 for all of Utah below 39.5°N
    #
    # counties not in any region: (none)
    # regions overlaying other regions: NU/North Utah, SU/South Utah
    # split counties: (none)
    #
    # Originally (2010) 2 regions NU and SU
    # 2011, NU and SU delineated by 39.5°N latitude. Some summits in NU marked as inactive, new summit references made in SU.
    # 2013, lots of new summits added. Added to new single-county regions. Old overlay regions remain.
    
    # BELOW IS ONLY FOR ACTIVE REFERENCES, NOT INACTIVE
    # Counties entirely in North region (13)
        # both in county region and North overlay region (13): Box Elder, Cache, Daggett, Davis, Duchesne, Morgan, Rich, Salt Lake, Summit, Tooele, Utah, Wasatch, Weber
        # only in county region: (none)
    # Counties in both regions (5)
        # only in North region and county region (2): Carbon, Uintah
        # in both North and South regions, and county region (3): Emery, Juab, Sanpete
    # Counties only in South region (11)
        # both in county region and South overlay region (11): Beaver, Garfield, Grand, Iron, Kane, Millard, Piute, San Juan, Sevier, Washington, Wayne
        # only in county region: (none)

    # {'identifier': 'NU', 'name': 'North Utah',                  'counties': ['Box Elder', 'Cache', 'Carbon', 'Daggett', 'Duchesne', 'Emery', 'Juab', 'Morgan', 'Rich', 'Salt Lake', 'Sanpete', 'Summit', 'Tooele', 'Uintah', 'Utah', 'Wasatch', 'Weber'] },
    {'identifier': 'W7U/NU', 'name': 'North Utah',  'type': 'state', 'state': 'UT', 'linesplit': [[(-179, 39.5), (179, 39.5)], 'N'] },

    # {'identifier': 'SU', 'name': 'South Utah',                  'counties': ['San Juan', 'Grand', 'Beaver', 'Sevier', 'Garfield', 'Wayne', 'Iron', 'Sanpete', 'Washington', 'Piute', 'Millard', 'Emery', 'Juab', 'Cache', 'Kane'] },
    {'identifier': 'W7U/SU', 'name': 'South Utah',  'type': 'state', 'state': 'UT', 'linesplit': [[(-179, 39.5), (179, 39.5)], 'S'] },

    {'identifier': 'W7U/BE', 'name': 'Beaver County',               'counties': ['UT_Beaver'] },
    {'identifier': 'W7U/BO', 'name': 'Box Elder County',            'counties': ['UT_Box Elder'] },
    {'identifier': 'W7U/CA', 'name': 'Cache County',                'counties': ['UT_Cache'] },
    {'identifier': 'W7U/CR', 'name': 'Carbon County',               'counties': ['UT_Carbon'] },
    {'identifier': 'W7U/DA', 'name': 'Daggett County',              'counties': ['UT_Daggett'] },
    {'identifier': 'W7U/DV', 'name': 'Davis County',                'counties': ['UT_Davis'] },
    {'identifier': 'W7U/DU', 'name': 'Duchesne County',             'counties': ['UT_Duchesne'] },
    {'identifier': 'W7U/EM', 'name': 'Emery County',                'counties': ['UT_Emery'] },
    {'identifier': 'W7U/GA', 'name': 'Garfield County',             'counties': ['UT_Garfield'] },
    {'identifier': 'W7U/GR', 'name': 'Grand County',                'counties': ['UT_Grand'] },
    {'identifier': 'W7U/IR', 'name': 'Iron County',                 'counties': ['UT_Iron'] },
    {'identifier': 'W7U/JU', 'name': 'Juab County',                 'counties': ['UT_Juab'] },
    {'identifier': 'W7U/KA', 'name': 'Kane County',                 'counties': ['UT_Kane'] },
    {'identifier': 'W7U/MI', 'name': 'Millard County',              'counties': ['UT_Millard'] },
    {'identifier': 'W7U/MO', 'name': 'Morgan County',               'counties': ['UT_Morgan'] },
    {'identifier': 'W7U/PI', 'name': 'Piute County',                'counties': ['UT_Piute'] },
    {'identifier': 'W7U/RI', 'name': 'Rich County',                 'counties': ['UT_Rich'] },
    {'identifier': 'W7U/SL', 'name': 'Salt Lake County',            'counties': ['UT_Salt Lake'] },
    {'identifier': 'W7U/SJ', 'name': 'San Juan County',             'counties': ['UT_San Juan'] },
    {'identifier': 'W7U/SP', 'name': 'Sanpete County',              'counties': ['UT_Sanpete'] },
    {'identifier': 'W7U/SE', 'name': 'Sevier County',               'counties': ['UT_Sevier'] },
    {'identifier': 'W7U/SM', 'name': 'Summit County',               'counties': ['UT_Summit'] },
    {'identifier': 'W7U/TO', 'name': 'Tooele County',               'counties': ['UT_Tooele'] },
    {'identifier': 'W7U/UI', 'name': 'Uintah County',               'counties': ['UT_Uintah'] },
    {'identifier': 'W7U/UT', 'name': 'Utah County',                 'counties': ['UT_Utah'] },
    {'identifier': 'W7U/WA', 'name': 'Wasatch County',              'counties': ['UT_Wasatch'] },
    {'identifier': 'W7U/WS', 'name': 'Washington County',           'counties': ['UT_Washington'] },
    {'identifier': 'W7U/WY', 'name': 'Wayne County',                'counties': ['UT_Wayne'] },
    {'identifier': 'W7U/WB', 'name': 'Weber County',                'counties': ['UT_Weber'] },

    # W7A: 21 regions, 15 counties
    # counties not in any region: (none)
    # regions overlaying other regions: AE/Eastern Arizona, AW/Western Arizona
    # split counties:  Coconino (35.7°N), Maricopa (33.45°N EXCEPT 1 error summit, MN-115 clearly supposed to be in MS), Mojave (35.2°N), Pima (112°W)
    {'identifier': 'W7A/AE', 'name': 'AZ-Eastern Arizona',      'counties': ['AZ_Coconino', 'AZ_Navajo', 'AZ_Apache', 'AZ_Graham', 'AZ_Greenlee', 'AZ_Cochise', 'AZ_Santa Cruz'] },
    {'identifier': 'W7A/AW', 'name': 'AZ-Western Arizona',      'counties': ['AZ_Mohave', 'AZ_Yavapai', 'AZ_La Paz', 'AZ_Yuma', 'AZ_Maricopa', 'AZ_Gila', 'AZ_Pinal', 'AZ_Pima'] },
    {'identifier': 'W7A/AP', 'name': 'Apache County',           'counties': ['AZ_Apache'] },
    {'identifier': 'W7A/CN', 'name': 'Coconino County, North',  'counties': ['AZ_Coconino'], 'linesplit': [[(-179, 35.7), (179, 35.7)], 'N'] },
    {'identifier': 'W7A/CS', 'name': 'Coconino County, South',  'counties': ['AZ_Coconino'], 'linesplit': [[(-179, 35.7), (179, 35.7)], 'S'] },
    {'identifier': 'W7A/CO', 'name': 'Cochise County',          'counties': ['AZ_Cochise'] },
    {'identifier': 'W7A/GI', 'name': 'Gila County',             'counties': ['AZ_Gila'] },
    {'identifier': 'W7A/GM', 'name': 'Graham County',           'counties': ['AZ_Graham'] },
    {'identifier': 'W7A/GR', 'name': 'Greelee County',          'counties': ['AZ_Greenlee'] },
    {'identifier': 'W7A/MN', 'name': 'Maricopa County, North',  'counties': ['AZ_Maricopa'], 'linesplit': [[(-179, 33.45), (179, 33.45)], 'N'] }, # 1 error summit
    {'identifier': 'W7A/MS', 'name': 'Maricopa County, South',  'counties': ['AZ_Maricopa'], 'linesplit': [[(-179, 33.45), (179, 33.45)], 'S'] },
    {'identifier': 'W7A/NA', 'name': 'Navajo County',           'counties': ['AZ_Navajo'] },
    {'identifier': 'W7A/NM', 'name': 'Northern Mohave County',  'counties': ['AZ_Mohave'], 'linesplit': [[(-179, 35.2), (179, 35.2)], 'N'] },
    {'identifier': 'W7A/SM', 'name': 'Southern Mohave County',  'counties': ['AZ_Mohave'], 'linesplit': [[(-179, 35.2), (179, 35.2)], 'S'] },
    {'identifier': 'W7A/PE', 'name': 'Pima County, East',       'counties': ['AZ_Pima'], 'linesplit': [[(-112, -89), (-112, 89)], 'E'] },
    {'identifier': 'W7A/PW', 'name': 'Pima County, West',       'counties': ['AZ_Pima'], 'linesplit': [[(-112, -89), (-112, 89)], 'W'] },
    {'identifier': 'W7A/PN', 'name': 'Pinal County',            'counties': ['AZ_Pinal'] },
    {'identifier': 'W7A/PZ', 'name': 'La Paz County',           'counties': ['AZ_La Paz'] },
    {'identifier': 'W7A/SC', 'name': 'Santa Cruz County',       'counties': ['AZ_Santa Cruz'] },
    {'identifier': 'W7A/YU', 'name': 'Yuma County',             'counties': ['AZ_Yuma'] },
    {'identifier': 'W7A/YV', 'name': 'Yavapai County',          'counties': ['AZ_Yavapai'] },

    # W4T: 4 regions, 95 counties
    # counties not in any region: (?)
    # regions overlaying other regions: (none)
    # split counties: Claiborne (error), Overton (split 85.3°W)
    {'identifier': 'W4T/CA', 'name': 'Cumberland - Appalachian Plateau',    'counties': ['TN_Overton'], 'linesplit': [[(-85.3, -89), (-85.3, 89)], 'E'], 'morecounties': ['TN_Franklin', 'TN_Marion', 'TN_Bledsoe', 'TN_Cumberland', 'TN_Morgan', 'TN_Scott', 'TN_Campbell', 'TN_Sequatchie', 'TN_Fentress'] },
    {'identifier': 'W4T/NB', 'name': 'Nashville Basin',                     'counties': ['TN_Overton'], 'linesplit': [[(-85.3, -89), (-85.3, 89)], 'W'], 'morecounties': ['TN_Smith', 'TN_Cannon', 'TN_Warren', 'TN_White', 'TN_Pickett'] },
    {'identifier': 'W4T/RV', 'name': 'Ridge and Valley',                    'counties': ['TN_Hamilton', 'TN_Rhea', 'TN_Anderson', 'TN_Roane', 'TN_Knox', 'TN_Claiborne', 'TN_Union', 'TN_Grainger', 'TN_Hancock', 'TN_Hamblen', 'TN_Hawkins', 'TN_Sullivan'] },
    {'identifier': 'W4T/SU', 'name': 'Smoky and Unaka Mountains',           'counties': ['TN_Polk', 'TN_Monroe', 'TN_Blount', 'TN_Sevier', 'TN_Cocke', 'TN_Greene', 'TN_Washington', 'TN_Unicoi', 'TN_Carter', 'TN_Johnson'] },

]

for ft in cgj["features"]:
    county_name = ft["properties"]["STUSPS"] + "_" + ft["properties"]["NAME"]
    counties_dict[county_name] = ft
    # e.g. { "WA_Grant": {...}, "WA_Clark": {...}, ... }



def construct_hull(regionfeature, regiondef):
    print(f'Constructing concave hull for "{regiondef['name']}"...', end='', flush=True)
    rgrows = []
    def is_region(row):
        if row['RegionName'] == regiondef['name']:
            vf = datetime.date.strptime(row['ValidFrom'], "%d/%m/%Y")
            vt = datetime.date.strptime(row['ValidTo'], "%d/%m/%Y")
            dt = datetime.date.today()
            return dt < vt and dt > vf
        return False
    with open(sys.argv[2], 'r') as sf:
        rd = csv.DictReader(sf)

        for row in filter(is_region, rd):
            rgrows.append(row)
    latlonlist = [(row['Longitude'], row['Latitude']) for row in rgrows]
    hull = shapely.concave_hull(shapely.MultiPoint(latlonlist), ratio=0.6)
    regionfeature["geometry"] = shapely.geometry.mapping(hull)
    print(' done')
    return


def construct_state(regionfeature, regiondef):
    state = regiondef["state"]
    counties_list = [x for x in counties_dict.keys() if x.split('_')[0] == state]

    rgshp = shapely.geometry.shape(regionfeature["geometry"])
    for county_name in counties_list:
        countyshp = shapely.geometry.shape(counties_dict[county_name]["geometry"])
        # print(f"about to merge {region['name']} with {county_name}")
        rgshp = shapely.coverage_union(rgshp, countyshp)
    regionfeature["geometry"] = shapely.geometry.mapping(rgshp)


def construct_counties(regionfeature, regiondef):
    counties_list = regiondef["counties"]
    if "NScounties" in regiondef: # TODO make command line option
        counties_list += regiondef["NScounties"]

    rgshp = shapely.geometry.shape(regionfeature["geometry"])
    for county_name in counties_list:
        countyshp = shapely.geometry.shape(counties_dict[county_name]["geometry"])
        # print(f"about to merge {region['name']} with {county_name}")
        rgshp = shapely.coverage_union(rgshp, countyshp)
    regionfeature["geometry"] = shapely.geometry.mapping(rgshp)


def handle_linesplit(regionfeature, regiondef):
    line = shapely.LineString(regiondef["linesplit"][0])   # 2 tuples, each one defines endpoint of a line
    direction = regiondef["linesplit"][1]                  # 'N', 'S', 'E', or 'W'
    rgshp = shapely.geometry.shape(regionfeature["geometry"])
    sidea, sideb = shapely.ops.split(rgshp, line).geoms
    keepside = rgshp

    # at this point we don't know which order shapely returned the sides in (e.g. west then east, or east then west) so we examine the points to figure it out
    idx = -1
    if direction == 'N' or direction == 'S':
        idx = 1 # look at the 2nd member of the tuple
    else:
        idx = 0 # look at the 1st member of the tuple

    found = False
    for point in sidea.exterior.coords:
        if point[idx] == regiondef["linesplit"][0][0][idx]:
            # this point is on the split line, it's not helpful for determining which side this polygon is on
            print('skipping point on line')
            continue
        else:
            if (direction == 'E' or direction == 'N') and point[idx] > regiondef["linesplit"][0][0][idx]:
                found = True
                print('keeping side a')
                keepside = sidea
            elif (direction == 'W' or direction == 'S') and point[idx] < regiondef["linesplit"][0][0][idx]:
                found = True
                print('keeping side a')
                keepside = sidea
            else:
                print('keeping side b')
                found = True
                keepside = sideb
            break
    if not found:
        print("Unable to determine which side of split to keep, quitting!")
        exit(3)

    regionfeature["geometry"] = shapely.geometry.mapping(keepside)


def handle_morecounties(regionfeature, regiondef):
    counties_list = regiondef["morecounties"]
    rgshp = shapely.geometry.shape(regionfeature["geometry"])
    for county_name in counties_list:
        countyshp = shapely.geometry.shape(counties_dict[county_name]["geometry"])
        # print(f"about to merge {region['name']} with {county_name}")
        rgshp = shapely.coverage_union(rgshp, countyshp)
    regionfeature["geometry"] = shapely.geometry.mapping(rgshp)



for regiondef in regions:
    rgft = copy.deepcopy(feature_template)
    rgft["properties"] = regiondef
    counties_list = []

    if "type" in regiondef and regiondef["type"] == "concave-hull":
        construct_hull(rgft, regiondef)

    elif "type" in regiondef and regiondef["type"] == "state":
        construct_state(rgft, regiondef)
        
    elif "counties" in regiondef:
        construct_counties(rgft, regiondef)

    if "linesplit" in regiondef:
        handle_linesplit(rgft, regiondef)

    if "morecounties" in regiondef:
        handle_morecounties(rgft, regiondef)

    gj_template["features"].append(rgft)


with open(sys.argv[3], 'w') as outf:
    json.dump(gj_template, outf)

print("done")

