https://www.sotadata.org.uk/en/logs/uniques/chaser/KK7LHY

under the hood, page calls https://api-db2.sota.org.uk/logs/uniques/chaser/83820/1/0
    - 83820 is userid for kk7lhy
    - 0 is sort by date
- prefaced by https://api-db2.sota.org.uk/logs/uniques/count/chaser/7798
    - 7798 is userid for ww7d
- requires auth
- request for next page (500) of results is https://api-db2.sota.org.uk/logs/uniques/chaser/7798/501/0
- sorting by association is https://api-db2.sota.org.uk/logs/uniques/chaser/7798/501/1
- sorting by chase count is https://api-db2.sota.org.uk/logs/uniques/chaser/7798/501/2

https://api-db2.sota.org.uk/logs/uniques/chaser/{userid}/{pagestartindex}/{sortmethod}
- userid: from https://api-db2.sota.org.uk/users/id/{callsign}
- pagestartindex: starts from 1, up to max specified by https://api-db2.sota.org.uk/logs/uniques/count/chaser/{userid}
- sortmethod: 0 for date, 1 for association, 2 for chase count


LOOKUP() function in libreoffice is kinda the key piece of this

export csv, import into google mymaps
https://www.google.com/maps/d/edit?mid=1g2_-MAskUVJt4kwqF6iI0o6pekl6mEo&usp=drive_link

