#!/usr/bin/env python

import os
import json
from datetime import datetime
import argparse
import matplotlib.pyplot as plt
import statistics

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--association-code', default='W7W')
args = parser.parse_args()

callsigns = {}

avgs_all = []
avgs_nonzero = []
avgs_twoplusdays = []
for filename in os.listdir(f"./data/{args.association_code}/by-call/"):
    with open(f"./data/{args.association_code}/by-call/{filename}", 'r') as f:
        curr_json = json.load(f)
        curr_call = curr_json['Callsign']

        valid_days = set()
        valid_points = 0
        for activation in curr_json['Activations']:
            if activation['SummitCode'][0:len(args.association_code)] == args.association_code:
                filtered_time = activation['firstQSO'].replace(' ', '').replace('+', '')
                if filtered_time[-2] == ':':
                    # only one character after the colon, somebody forgot the last minute digit
                    filtered_time = filtered_time + '0'
                activ_date_time = f"{activation['ActivationDate']} {filtered_time}"
                activ_utc = datetime.fromisoformat(activ_date_time+'+00:00')
                # assume that the time zone of the activation is the same as the time zone of the current computer
                # i.e. if you live in W7W and are trying to calculate the record for W7W, all is well
                # but if you live in W7W and are trying to calculate the record for HB, you will need to modify this
                activ_local = activ_utc.astimezone()
                activ_local_day = activ_local.strftime('%Y-%m-%d')
                valid_days.add(activ_local_day)

                valid_points += activation['Points'] + activation['BonusPoints']

        if len(valid_days):
            avg_per_day = valid_points / len(valid_days)
        else:
            avg_per_day = 0
        print(f"{curr_call}: {avg_per_day}")
        avgs_all.append(avg_per_day)
        if avg_per_day:
            avgs_nonzero.append(avg_per_day)
        if len(valid_days) >= 2:
            avgs_twoplusdays.append(avg_per_day)

med_all = statistics.median(avgs_all)
med_nonzero = statistics.median(avgs_nonzero)
med_twoplusdays = statistics.median(avgs_twoplusdays)

with open(f"./data/{args.association_code}/date.txt", 'r') as f:
    data_as_of = f.read().strip()

legend, histogram = plt.subplots()
histogram.hist(avgs_all, bins=20, color='xkcd:purple', edgecolor='k')
histogram.set_title(f"SOTA Points per Day for {args.association_code} activators (as of {data_as_of})")
histogram.set_xlabel("Average Points per Day")
histogram.set_ylabel("Count of Activators")

min_ylim, max_ylim = plt.ylim()
histogram.axvline(med_all, color='xkcd:bright red', label=f"Median ({len(avgs_all)} activators): {med_all}")
histogram.axvline(med_nonzero, color='xkcd:bright yellow', label=f"Median (excluding activators with average of 0) ({len(avgs_nonzero)}): {med_nonzero}")
histogram.axvline(med_twoplusdays, color='xkcd:bright green', label=f"Median (excluding activators with less than 2 days) ({len(avgs_twoplusdays)}): {med_twoplusdays}")

legend.legend()

plt.show()

