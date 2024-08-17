#!/usr/bin/env python

import os
import json
from datetime import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--association',      default='W7W')
parser.add_argument('-l', '--leaderboard-size', default=10, type=int)
args = parser.parse_args()

callsigns = {}

for filename in os.listdir('./data/by-call/'):
    with open(f"./data/by-call/{filename}", 'r') as f:
        curr_json = json.load(f)
        curr_call = curr_json[0]['OwnCallsign']
        callsigns[curr_call] = {}
        for activation in curr_json:
            filtered_time = activation['firstQSO'].replace(' ', '').replace('+', '')
            activ_date_time = f"{activation['ActivationDate']} {filtered_time}"
            activ_utc = datetime.fromisoformat(activ_date_time+'+00:00')
            # assume that the time zone of the activation is the same as the time zone of the current computer
            # i.e. if you live in W7W and are trying to calculate the record for W7W, all is well
            # but if you live in W7W and are trying to calculate the record for HB, you will need to modify this
            activ_local = activ_utc.astimezone()
            activ_local_day = activ_local.strftime('%Y-%m-%d')
            if activ_local_day in callsigns[curr_call]:
                callsigns[curr_call][activ_local_day].append(activation)
            else:
                callsigns[curr_call][activ_local_day] = [activation]

top_n = [(0, 'fakecall', 'fakedate')]

for callsign in callsigns:
    for date in callsigns[callsign]:
        filtered = filter(lambda a: a['SummitCode'][0:len(args.association)] == args.association, callsigns[callsign][date])
        curr_points = sum([activation['Points'] + activation['BonusPoints'] for activation in filtered])

        min_points = top_n[-1][0]
        if curr_points == min_points:
            top_n.append((curr_points, callsign, date))
        elif curr_points > min_points:
            top_n.append((curr_points, callsign, date))
            top_n.sort(key=lambda tup: tup[0], reverse=True)
            if len(top_n) > args.leaderboard_size:
                min_points_to_keep = top_n[args.leaderboard_size - 1][0]
                while top_n[-1][0] < min_points_to_keep:
                    top_n.pop()

print(top_n)

for item in top_n:
    max_print = json.dumps(callsigns[item[1]][item[2]], indent=4)
    print(item)
    print(max_print)

