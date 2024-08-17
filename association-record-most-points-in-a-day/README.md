general idea:
- grab_data.py
    - request list of all activators in association
    - use parameter for a rough guess of the record of most points in a day within the association
        - request and save the log of each activator with at least that number of points to json file
- process_data.py
    - for each activator:
        - iterate through logfile to make a dictionary of day:activations
    - create leaderboard
    - for each activator, for each day:
        - throw away activations not in the association
        - tally up points for that day
        - add to leaderboard if in top N
        - prune leaderboard

top 10(+ ties) for W7W as of 2024-08-15:
[(34, 'WW7D', '2019-08-24'), (34, 'LA/WU7H/P', '2019-08-24'),
(32, 'WX7EMT', '2017-10-09'), (32, 'LA/WU7H/P', '2017-10-09'),
(30, 'NN7M', '2022-09-27'), (30, 'KK7LHY/P', '2023-10-21'), (30, 'KJ7RTO', '2022-06-21'),
(28, 'WW7D', '2023-07-17'), (28, 'WW7D', '2022-09-04'), (28, 'WW7D', '2021-08-19'), (28, 'WW7D', '2018-07-01'), (28, 'WW7D', '2016-07-10'), (28, 'LA/WU7H/P', '2022-09-04')]

top 10(+ ties) for W7O as of 2024-08-16:
[(30, 'K7ATN', '2014-07-26'),
(28, 'KG7JQY', '2024-07-27'),
(27, 'ND7PA', '2016-12-03'),
(26, 'K7WXW', '2023-07-22'), (26, 'KG7JQY', '2024-07-29'), (26, 'K7HY', '2023-07-23'), (26, 'NE7ET', '2023-07-23'), (26, 'N7KOM', '2022-07-09'),
(25, 'KK7LVA', '2023-12-26'), (25, 'ND7PA', '2015-01-31'), (25, 'K7AGL', '2022-03-26')]

top 10(+ ties) for W7I as of 2024-08-16:
[(24, 'K7MK', '2023-09-01'), (24, 'K7MK', '2023-07-29'), (24, 'K7MK', '2019-07-03'), (24, 'KF7DDT', '2013-06-29'), (24, 'KG7VLX', '2023-10-20'), (24, 'N0DNF', '2023-06-17'),
(22, 'KG7VLX', '2023-09-04'), (22, 'KG7VLX', '2021-09-18'),
(21, 'N0DNF', '2021-12-01'),
(18, 'K7ZO', '2015-07-31'), (18, 'K7MK', '2020-09-07'), (18, 'K7MK', '2019-07-02'), (18, 'K7MK', '2015-07-31'), (18, 'KF7DDT', '2014-07-06'), (18, 'KC3GOP', '2023-09-02'), (18, 'KC3GOP', '2023-06-15'), (18, 'KC3GOP', '2021-03-15'), (18, 'W7IMC', '2014-08-01'), (18, 'W7IMC', '2014-06-29'), (18, 'N0DNF', '2024-07-15'), (18, 'N0DNF', '2022-06-05'), (18, 'KG7KMV', '2021-10-09'), (18, 'KJ7GRQ', '2022-06-05')]

