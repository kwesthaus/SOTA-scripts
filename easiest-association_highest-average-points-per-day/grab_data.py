#!/usr/bin/env python

import requests
import time
import datetime
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--association-code', default='W7W')
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



url = f"https://api-db.sota.org.uk/admin/activator_roll?associationID={association_id}"
print(url)
r2 = requests.get(url)
print(f"\t{r2.status_code}")

with open(f"./data/{args.association_code}/activator_roll.json", 'w') as f:
    f.write(r2.text)



activators_raw = r2.json()
total = len(activators_raw)
print(f"Starting to download logs for each of the {total} activators with home association set to {args.association_code}")
idx = 0
# skip = 1
for activator in activators_raw:
    idx += 1
    call = activator['Callsign']
    # if call != 'kj7knr' and skip:
    #     continue
    # elif call == 'kj7knr':
    #     print('continuing from kj7knr')
    #     skip = 0

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

with open(f"./data/{args.association_code}/date.txt", 'w') as f:
    f.write(str(datetime.datetime.now()))

