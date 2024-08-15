general idea:
- grab_data.py
    - request honor roll page
    - for each activator:
        - request log, save to json file
- draw_graph.py
    - iterate over log file for each activator
        - iterate over all activations, filtering out those that don't meet our criteria for points, and make a series of (day of year, SOTA points) datapoints
    - sort activators by final # of points and keep top N
    - add lines of datapoints to the graph

Example output:
![example line graph](2024-08-14.png)

