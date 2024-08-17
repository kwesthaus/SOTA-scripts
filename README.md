# SOTA-scripts
Play with data from the Summits on the Air program

These scripts all expect a bearer token to be placed in `bearer_token.txt` to be used to access the authorization-required API endpoints. You can copy this header out of the network tab in the dev tools of firefox while logged in to the SOTA website. Occasionally it will expire in the middle of grabbing data - more logic could be added to handle refreshing the token, but that hasn't been implemented yet.

