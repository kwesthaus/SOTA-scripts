#!/usr/bin/env python

# Known Limitations
## requires manual download + deletion of first line of summitslist.csv
## requires user to grab Auth token from browser dev tools
## requires a google account for google mymaps, ideally would be possible to get working with leaflet as well
## google mymaps limits to 2,000 point markers per layer, so we have to make a new file every 2,000 points


import argparse
import requests
import json
import time
import csv

parser = argparse.ArgumentParser()
parser.add_argument('callsign') # e.g. "KK7LHY"
parser.add_argument('summitscsv') # path to summitslist csv with non-csv-conformant first line removed, e.g. "./summitslist.csv"
parser.add_argument('outprefix') # path prefix for output files (new file for every 2,000 points due to google mymaps limitation), e.g. "./mychased" -> ./mychased_1.csv, ./mychased_2.csv
parser.add_argument('-r', '--rate-limit', default=1, type=int)
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
    "Host": "api-db2.sota.org.uk",
    "Origin": "https://www.sotadata.org.uk",
    "Referer": "https://www.sotadata.org.uk/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Sec-GPC": "1",
    "TE": "trailers",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
}



url = f"https://api-db2.sota.org.uk/users/id/{args.callsign}"
print(url)
r = requests.get(url, headers=h)
print(f"\t{r.status_code}")
uid = r.json()['id']
print(uid)
print()

url = f"https://api-db2.sota.org.uk/logs/uniques/count/chaser/{uid}"
print(url)
r = requests.get(url, headers=h)
print(f"\t{r.status_code}")
count = r.json()
print(count)
print()

pages = (count // 500) + 1
sortmethod = 1 # by association - this means we can step through the summitslist in order, without having to search the entire list each time
chased = []
for i in range(pages):
    pagestartindex = (500 * i) + 1
    url = f"https://api-db2.sota.org.uk/logs/uniques/chaser/{uid}/{pagestartindex}/{sortmethod}"
    print(f"{pagestartindex} of {count}")
    r = requests.get(url, headers=h)
    print(f"\t{r.status_code}")
    chased += r.json()
    print()

    # rate limit ourselves to avoid hitting the servers too hard
    time.sleep(args.rate_limit)

# format: {'FirstActivationDate': '2021-03-06', 'Activationcount': 1, 'Summit': 'JA/HG-082 (Kurozuhou)', 'Number': 1}

outfileidx = 1
outfilename = args.outprefix + f"_{outfileidx}.csv"
with open(args.summitscsv, 'r') as inf, open(outfilename, 'w') as outf:
    rd = csv.DictReader(inf)
    fn = ['Order', 'SummitCode', 'SummitName', 'Lat', 'Long', 'ChaseCount', 'FirstChaseDate']
    wt = csv.DictWriter(outf, fn)
    wt.writeheader()

    for summit in chased:
        code,name = summit['Summit'].split(' ', 1)
        if name[0] != '(' or name[-1] != ')':
            print('Unexpected Summit string format, quitting!')
            exit(1)
        name = name[1:-1]

        row = next(rd)
        while row['SummitCode'] != code:
            row = next(rd)
        
        curr = {
                'Order': summit['Number'],
                'SummitCode': code,
                'SummitName': name,
                'Lat': row['Latitude'],
                'Long': row['Longitude'],
                'ChaseCount': summit['Activationcount'],
                'FirstChaseDate': summit['FirstActivationDate']
        }
        wt.writerow(curr)
        if not curr['Order'] % 500:
            print(f"{curr['Order']} of {count}")
        if not curr['Order'] % 2000:
            # time for a new file
            outf.close()
            outfileidx += 1
            outfilename = args.outprefix + f"_{outfileidx}.csv"
            outf = open(outfilename, 'w')
            wt = csv.DictWriter(outf, fn)
            wt.writeheader()
            

print('done')

