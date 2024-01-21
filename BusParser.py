from google.transit import gtfs_realtime_pb2
from urllib.request import urlopen
from urllib.error import URLError
import datetime

import requests
import zipfile
import pandas as pd
from io import BytesIO

from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer


#print("Hello World")
# try:
#     print("Trying to reach the server...")
#     feed = gtfs_realtime_pb2.FeedMessage()
#     response = urlopen('https://webapps.regionofwaterloo.ca/api/grt-routes/api/vehiclepositions')
#     feed.ParseFromString(response.read())
#     print("Successfully reached the server!")
#     print(feed.entity)
#     for entity in feed.entity:
#         if entity.HasField('trip_update'):
#             print(entity.trip_update)
# except URLError as e:
#     print(f"Failed to reach the server: {e.reason}")
# except Exception as e:
#     print(f"An error occurred: {e}")


    # Download the file
response = requests.get('https://www.regionofwaterloo.ca/opendatadownloads/GRT_GTFS.zip')
z = zipfile.ZipFile(BytesIO(response.content))
filenames = z.namelist()
dfs = []
# Extract and parse each CSV file in the zip file
for filename in z.namelist():
    if filename.endswith('.txt'):
        df = pd.read_csv(z.open(filename))
        dfs.append(df)
        #print(f"Contents of {filename}:")
        #print(df)

# Use the function with a URL
bus_num = "201"

#find routet.txt in filenames and index dfs
route_df = dfs[filenames.index('routes.txt')]
#print(type(route_df), route_df)
bus_route_id = 201
bus_direction_id = 0
trip_df = dfs[filenames.index('trips.txt')]
bus_trips = trip_df[trip_df['route_id'].isin([bus_route_id])]
#print(bus_trips.head())
filtered_trips = trip_df[(trip_df['route_id'] == bus_route_id) & (trip_df['direction_id'] == bus_direction_id)]

#print(bus_trips.head())
stop_times_df = dfs[filenames.index('stop_times.txt')]

stops_df = dfs[filenames.index('stops.txt')]

stop_name = 'Hazel / Columbia'
stop_id = 2512
stop_id2 = 2524

#

trip_ids = filtered_trips['trip_id']
#print(type(trip_ids))
# Filter the stop_times_df DataFrame based on trip_id
filtered_stop_times = stop_times_df[stop_times_df['trip_id'].isin(trip_ids)]
stop_ids = filtered_stop_times['stop_id']
#print(type(stop_ids))

#sprint(stop_ids)
#filtered_stops = stops_df[stops_df['stop_id'].isin(stop_ids)]
#print(filtered_stops)

# Get the stop names
#stop_names = filtered_stops['stop_name']

# Print the stop names
#print(stop_names)


#filtered_stop_times.to_csv('filtered_stop_times.csv', index=False)


filtered_stop_times = filtered_stop_times[filtered_stop_times['stop_id'] == stop_id2]

now = datetime.datetime.now().time()

#print(filtered_stop_times['arrival_time'])
filtered_stop_times['arrival_time'].to_csv('arrival_times.csv', index=False)

filtered_stop_times['arrival_time'] = filtered_stop_times['arrival_time'].str.replace('^24', '00')
filtered_stop_times['arrival_time'] = pd.to_datetime(filtered_stop_times['arrival_time']).dt.time

next_bus_time = filtered_stop_times[filtered_stop_times['arrival_time'] > now]['arrival_time'].min()
time_difference = datetime.datetime.combine(datetime.date.today(), next_bus_time) - datetime.datetime.combine(datetime.date.today(), now)
print(time_difference)


class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Get dynamic data from Python
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Next Bus</title>
            </head>
            <body>
                <h1>Next Bus</h1>
                <p>The next bus will arrive in: {time_difference}</p>
            </body>
            </html>
            """

            # Read and send the HTML file with dynamic data
            # with open('index.html', 'w') as f:
            #     f.write(html_content)
            self.wfile.write(html_content.encode())

        else:
            return SimpleHTTPRequestHandler.do_GET(self)

PORT = 8000

with TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()


#filtered_df = stop_times_df[stop_times_df['stop_id'] == 1171]

# Print the filtered DataFrame
#print(filtered_stop_times)



#print(bus_route_id)
