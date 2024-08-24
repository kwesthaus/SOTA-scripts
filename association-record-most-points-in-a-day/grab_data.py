#!/usr/bin/env python

import requests
import time
import datetime
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--association-code', default='W7W')
parser.add_argument('-m', '--minimum-points',   default=20, type=int)
parser.add_argument('-s', '--skip-to-call',     default='')
parser.add_argument('-r', '--rate-limit',       default=1, type=int)
args = parser.parse_args()

auth_header = ''
with open('bearer_token.txt', 'r') as f:
    auth_header = f.read().strip()

h = {
    "Accept": "application/json, text/plain, */*",
	"Accept-Encoding": "gzip, deflate, br",
	"Accept-Language": "en-US,en;q=0.5",
    "Authorization": auth_header,
    "Connection": "keep-alive",
    "DNT": "1",
    "Host": "api-db.sota.org.uk",
    "Origin": "https://www.sotadata.org.uk",
    "Referer": "https://www.sotadata.org.uk/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Sec-GPC": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0",
}



url = "https://api-db2.sota.org.uk/associations"
print(url)
r = requests.get(url)
print(f"\t{r.status_code}")
associations_raw = r.json()

association_id = ''
for association in associations_raw:
    if association['code'] == args.association_code:
        association_id = association['id']
if not association_id:
    print(f"Could not find association for code {args.association_code}, quitting!")
    exit(1)



# if we are continuing a previous download run, don't download the activator roll again in case it has changed
if not args.skip_to_call:
    url = f"https://api-db.sota.org.uk/admin/activator_roll?associationID={association_id}"
    print(url)
    r2 = requests.get(url)
    print(f"\t{r2.status_code}")

    with open(f"./data/{args.association_code}/activator_roll.json", 'w') as f:
        f.write(r2.text)

activators_raw = ''
with open(f"./data/{args.association_code}/activator_roll.json", 'r') as f:
    activators_raw = json.load(f)



total = len(activators_raw)
print(f"Starting to process each of the {total} activators with home association set to {args.association_code}")
idx = 0
found = False
num_over = 0
num_under = 0
for activator in activators_raw:
    idx += 1
    # remove any postfixes, e.g. N1WGU/P
    call = activator['Callsign'].split('/')[0]
    if args.skip_to_call:
        if not found:
            if call != args.skip_to_call:
                continue
            else:
                print(f"continuing from {args.skip_to_call}")
                found = True

    if activator['totalPoints'] >= args.minimum_points:
        num_over += 1
        # rate limit ourselves to avoid hitting the servers too hard
        time.sleep(args.rate_limit)

        uid = activator['UserID']
        print(f"({idx} / {total}). {call} ({uid}): {activator['totalPoints']}")
        # doesn't have firstQSO field that we need to adjust for local time
        # url = f"https://api-db2.sota.org.uk/logs/activator/{activator['UserID']}/9999/0"
        url = f"https://api-db.sota.org.uk/admin/secure/activator_log_by_id?year=all&desc=1&id={uid}"
        print(f"\t{url}")

        r3 = requests.get(url, headers=h)
        print(f"\t{r3.status_code}")
        if r3.status_code == 401:
            print("Unauthorized, bearer token probably expired, quitting!")
            exit(1)
        activator['Activations'] = r3.json()
        with open(f"./data/{args.association_code}/by-call/{call}.json", 'w') as f:
            json.dump(activator, f)

    else:
        num_under += 1

with open(f"./data/{args.association_code}/date.txt", 'w') as f:
    f.write(str(datetime.datetime.now()))

# count is only accurate if we didn't start partway through
if not args.skip_to_call:
    print(f"{num_over} activators over the minimum point value and {num_under} activators under")

