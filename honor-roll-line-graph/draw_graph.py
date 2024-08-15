#!/usr/bin/env python

import os
import json
import datetime
from collections import OrderedDict
import argparse

import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('-y', '--year',             default=2024, type=int)
parser.add_argument('-a', '--association',      default='W7W')
parser.add_argument('-l', '--leaderboard-size', default=15, type=int)
args = parser.parse_args()

# dictionary from callsign to dictionary
# inner dictionary dayOfYear: pointsSoFar
callsigns = {}

curr_json = ''
final_date = datetime.datetime.utcnow().date() + datetime.timedelta(days=1) - datetime.date(args.year, 1, 1)
final_dayofyear = final_date.days
idx = 1

files = os.listdir('./data/by-call/')
# no longer needed because we now sort after creating the dictionary but before adding to the plot
# files.sort()
for filename in files:
    total_points = 0

    # open file, create corresponding dictionary key
    with open(F"./data/by-call/{filename}", 'r') as f:
        curr_json = json.load(f)
        curr_call = curr_json[0]['OwnCallsign']
        callsigns[curr_call] = {}

    # we rely on the sota api giving us activations in date order so that keeping track of the number of points we've seen so far is monotonically increasing
    for activation in curr_json:
        # TODO: abstract this out to filter based on cmdline arguments
        # # exclude activations without a qualifying number of 2meter and a qualifying number of fm contacts
        # # yes, this means that you can make only 4 (2m&ssb) contacts and 4 (70cm&fm) contacts and have that count
        # # but modifying this script to check the actual contacts to make sure 4 (2m&fm) contacts were made is a lot of effort so I haven't done that yet
        # if activation['QSO2'] < 4 or activation['QSOfm'] < 4:
        #     continue
        # if activation['QSO2'] != activation['QSOfm'] and activation['QSO2'] + activation['QSO70c'] != activation['QSOfm']:
        #     print('interesting!')
        #     print(activation)
        #     print()
        # all associations have different point rules, compare just within Washington for a level playing field
        if activation['SummitCode'][0:3] != args.association:
            continue
        # VHF and higher (above 23cm isn't included in the general log page)
        # if activation['QSO6'] + activation['QSO4'] + activation['QSO2'] + activation['QSO70c'] + activation['QSO23c'] < 4:
        #     continue
        # 
        # if we do it instead by removing HF contacts, we include everything above 23cm at the expense of including VLF contacts
        # I verified that there are no VLF contacts in W7W in 2023 as of 2023-09-06, but that is not true of every year
        if activation['QSOs'] - activation['QSO160'] - activation['QSO80'] - activation['QSO60'] - activation['QSO40'] - activation['QSO30'] - activation['QSO20'] - activation['QSO17'] - activation['QSO15'] - activation['QSO12'] - activation['QSO10'] < 4:
            continue

        # calculate day of year as X coordinate
        curr_raw_date = [int(x) for x in activation['ActivationDate'].split('-')]
        curr_date = datetime.date(*curr_raw_date)
        curr_diff = curr_date - datetime.date(args.year, 1, 1)
        curr_dayofyear = curr_diff.days

        # calculate, then update or set, Y coordinate based on points
        total_points += activation['Points'] + activation['BonusPoints']
        callsigns[curr_call][curr_dayofyear] = total_points

    # make all the lines end at the same horizontal position on the graph for easier visual comparison of close scores
    callsigns[curr_call][final_dayofyear] = total_points

print(json.dumps(callsigns, sort_keys=False, indent=4))
print(len(callsigns))

fig, ax = plt.subplots()

sorted_calls = OrderedDict(sorted(callsigns.items(), reverse=True, key=lambda item: item[1][final_dayofyear]))
print(sorted_calls)

idx = 1
# convert dictionary to 2 lists cause that's what matplotlib wants
for call in sorted_calls:
    if idx > args.leaderboard_size:
        break

    days = callsigns[call].keys()
    points = callsigns[call].values()
    ax.plot(days, points, label=f"{idx}. {call}: {callsigns[call][final_dayofyear]}")
    idx += 1

with open("./data/date.txt", 'r') as f:
    data_as_of = f.read().strip()

ax.set_title(f"{args.year} SOTA Honour Roll: {args.association} Activations Scored using only VHF-and-above Contacts (as of {data_as_of})")
ax.set_xlabel("Day of Year")
ax.set_ylabel("Points")
fig.legend()
plt.show()

