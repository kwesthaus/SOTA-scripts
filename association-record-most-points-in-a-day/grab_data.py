#!/usr/bin/env python

import requests
import time
import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--association-code', default='65') # W7W
parser.add_argument('-m', '--minimum-points',   default=20, type=int)
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

url = f"https://api-db.sota.org.uk/admin/activator_roll?associationID={args.association_code}"
print(url)
r = requests.get(url)
activators_raw = r.json()

num_over = 0
num_under = 0
for activator in activators_raw:
    if activator['totalPoints'] >= args.minimum_points:
        num_over += 1
        # rate limit ourselves to avoid hitting the servers too hard
        time.sleep(args.rate_limit)

        call = activator['Callsign']
        uid = activator['UserID']
        print(f"{call} ({uid}): {activator['totalPoints']}")
        url = f"https://api-db.sota.org.uk/admin/secure/activator_log_by_id?year=all&desc=1&id={activator['UserID']}"
        print(f"\t{url}")

        r2 = requests.get(url, headers=h)
        print(f"\t{r2.status_code}")
        with open(f"./data/by-call/{call}.json", 'w') as f:
            f.write(r2.text)

    else:
        num_under += 1

with open("./data/date.txt", 'w') as f:
    f.write(str(datetime.datetime.now()))

print(f"{num_over} activators over the minimum point value and {num_under} activators under")

