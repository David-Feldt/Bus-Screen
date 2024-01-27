from google.transit import gtfs_realtime_pb2
from urllib.request import urlopen
from urllib.error import URLError
import datetime

import requests
import zipfile
import pandas as pd
from io import BytesIO

from http.server import SimpleHTTPRequestHandler
from http.server import BaseHTTPRequestHandler

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
#response = requests.get('https://www.regionofwaterloo.ca/opendatadownloads/GRT_GTFS.zip')
#z = zipfile.ZipFile(BytesIO(response.content))
z = zipfile.ZipFile('./GRT_GTFS.zip','r')
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
route_df = dfs[filenames.index('routes.txt')]
bus_route_id_201 = 201
bus_route_id_19 = 19
bus_route_id_7 = 7
bus_route_id_301 = 301
bus_route_id_31 = 31

trip_df = dfs[filenames.index('trips.txt')]

# TODO combine 31 and 201 only have weekeday schedule

calendar_dates_df = dfs[filenames.index('calendar_dates.txt')]
now = datetime.datetime.now()

# Format the date as YYYYDDMM
date_of_interest = int(now.strftime('%Y%m%d'))
#date_of_interest = 20240126
print("Date of interest",date_of_interest)
filtered_calendar_dates = calendar_dates_df[calendar_dates_df['date'] == date_of_interest]
service_ids = filtered_calendar_dates['service_id'].unique()
print("Service id",service_ids)

#  ONLY HAVE WITH CORRECT SERVIE_ID
filtered_trips_201W = trip_df[((trip_df['route_id'] == bus_route_id_201) | (trip_df['route_id'] == bus_route_id_31)) & (trip_df['direction_id'] == 0) & (trip_df['service_id'].isin(service_ids))]
filtered_trips_19S = trip_df[(trip_df['route_id'] == bus_route_id_19) & (trip_df['direction_id'] == 0) & (trip_df['service_id'].isin(service_ids))]
filtered_trips_7S = trip_df[(trip_df['route_id'] == bus_route_id_7) & (trip_df['direction_id'] == 0) & (trip_df['service_id'].isin(service_ids))]
filtered_trips_201E = trip_df[((trip_df['route_id'] == bus_route_id_201) | (trip_df['route_id'] == bus_route_id_31)) & (trip_df['direction_id'] == 1) & (trip_df['service_id'].isin(service_ids))]
filtered_trips_301S = trip_df[(trip_df['route_id'] == bus_route_id_301) & (trip_df['direction_id'] == 0) & trip_df['service_id'].isin(service_ids)]
filtered_trips_301N = trip_df[(trip_df['route_id'] == bus_route_id_301) & (trip_df['direction_id'] == 1) & trip_df['service_id'].isin(service_ids)]
#print(bus_trips.head())

stop_times_df = dfs[filenames.index('stop_times.txt')]
stops_df = dfs[filenames.index('stops.txt')]

stop_name = 'Hazel / Columbia'
stop_idN = 3623
stop_idS = 1171
stop_idE =  2512
stop_idW = 2524
stop_id7 = 1915 #2509 #4073
stop_id301N = 6120
stop_id301S = 6004

trip_ids_201W = filtered_trips_201W['trip_id']
trid_ids_19S = filtered_trips_19S['trip_id']
trip_ids_7S = filtered_trips_7S['trip_id']
trip_ids_201E = filtered_trips_201E['trip_id']
trip_ids_301N = filtered_trips_301N['trip_id']
trip_ids_301S = filtered_trips_301S['trip_id']

#print(type(trip_ids))
# Filter the stop_times_df DataFrame based on trip_id
filtered_stop_times_201W = stop_times_df[stop_times_df['trip_id'].isin(trip_ids_201W)]
filtered_stop_times_19S = stop_times_df[stop_times_df['trip_id'].isin(trid_ids_19S)]
filtered_stop_times_7S = stop_times_df[stop_times_df['trip_id'].isin(trip_ids_7S)]
filtered_stop_times_201E = stop_times_df[stop_times_df['trip_id'].isin(trip_ids_201E)]
filtered_trips_301S = stop_times_df[stop_times_df['trip_id'].isin(trip_ids_301S)]
filtered_trips_301N = stop_times_df[stop_times_df['trip_id'].isin(trip_ids_301N)]


stop_ids_201W = filtered_stop_times_201W['stop_id']
stop_ids_19S = filtered_stop_times_19S['stop_id']
stop_ids_7S = filtered_stop_times_7S['stop_id']
stop_ids_201E = filtered_stop_times_201E['stop_id']
stop_id301S = filtered_trips_301S['stop_id']
stop_id301N = filtered_trips_301N['stop_id']

filtered_stop_times_201W = filtered_stop_times_201W[filtered_stop_times_201W['stop_id'] == stop_idW]
filtered_stop_times_19S = filtered_stop_times_19S[filtered_stop_times_19S['stop_id'] == stop_idS]
filtered_stop_times_201E = filtered_stop_times_201E[filtered_stop_times_201E['stop_id'] == stop_idE]
filtered_stop_times_7S = filtered_stop_times_7S[filtered_stop_times_7S['stop_id'] == stop_id7]
filtered_trips_301S = filtered_trips_301S[filtered_trips_301S['stop_id'] == stop_id301S]
filtered_trips_301N = filtered_trips_301N[filtered_trips_301N['stop_id'] == stop_id301N]

#print(filtered_stop_times['arrival_time'])
filtered_stop_times_201W.to_csv('stop_times_201W.csv', index=False)

filtered_stop_times_201W['arrival_time'] = filtered_stop_times_201W['arrival_time'].str.replace('^24', '00')
filtered_stop_times_201E['arrival_time'] = filtered_stop_times_201E['arrival_time'].str.replace('^24', '00')
filtered_stop_times_19S['arrival_time'] = filtered_stop_times_19S['arrival_time'].str.replace('^24', '00')
filtered_stop_times_7S['arrival_time'] = filtered_stop_times_7S['arrival_time'].str.replace('^24', '00')
filtered_trips_301N['arrival_time'] = filtered_trips_301N['arrival_time'].str.replace('^24', '00')
filtered_trips_301S['arrival_time'] = filtered_trips_301S['arrival_time'].str.replace('^24', '00')

filtered_stop_times_201W['arrival_time'] = pd.to_datetime(filtered_stop_times_201W['arrival_time']).dt.time
filtered_stop_times_201E['arrival_time'] = pd.to_datetime(filtered_stop_times_201E['arrival_time']).dt.time
filtered_stop_times_19S['arrival_time'] = pd.to_datetime(filtered_stop_times_19S['arrival_time']).dt.time
filtered_stop_times_7S['arrival_time'] = pd.to_datetime(filtered_stop_times_7S['arrival_time']).dt.time
filtered_trips_301S['arrival_time'] = pd.to_datetime(filtered_trips_301S['arrival_time']).dt.time
filtered_trips_301N['arrival_time'] = pd.to_datetime(filtered_trips_301N['arrival_time']).dt.time

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
    #if self.path == '/':
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Get dynamic data from Python
        now = datetime.datetime.now().time()
        next_bus_time_201W = filtered_stop_times_201W[filtered_stop_times_201W['arrival_time'] > now]['arrival_time'].min()
        next_bus_time_19S = filtered_stop_times_19S[filtered_stop_times_19S['arrival_time'] > now]['arrival_time'].min()
        next_bus_time_7S = filtered_stop_times_7S[filtered_stop_times_7S['arrival_time'] > now]['arrival_time'].min()
        next_bus_time_301S = filtered_trips_301S[filtered_trips_301S['arrival_time'] > now]['arrival_time'].min()
        next_bus_time_301N = filtered_trips_301N[filtered_trips_301N['arrival_time'] > now]['arrival_time'].min()
        time_7S = datetime.datetime.combine(datetime.date.today(), next_bus_time_7S) - datetime.datetime.combine(datetime.date.today(), now)
        time_201W = datetime.datetime.combine(datetime.date.today(), next_bus_time_201W) - datetime.datetime.combine(datetime.date.today(), now)
        time_19S = datetime.datetime.combine(datetime.date.today(), next_bus_time_19S) - datetime.datetime.combine(datetime.date.today(), now)
        time_301N = datetime.datetime.combine(datetime.date.today(), next_bus_time_301N) - datetime.datetime.combine(datetime.date.today(), now)
        time_301S = datetime.datetime.combine(datetime.date.today(), next_bus_time_301S) - datetime.datetime.combine(datetime.date.today(), now)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Next Bus</title>
            <meta http-equiv="refresh" content="5">
        </head>
        <body>
            <div class="card" style="width: 90%; padding: 20px; border: 3px solid #000; border-radius: 3px; margin: 10px; display: flex; flex-direction: row; justify-content: space-between;align-items: center;">
            <div class="left-text" stlye ="flex: 1;">
                <h2>201 - W</h2>
            </div>
            <div class="right-text" style="flex: 1; text-align: right;">
                <h3>{time_201W} mins</h3>
            </div>
            </div>
            <div class="card" style="width: 90%; padding: 20px; border: 3px solid #000; border-radius: 3px; margin: 10px; display: flex; flex-direction: row; justify-content: space-between;align-items: center;">
            <div class="left-text" stlye ="flex: 1;">
                <h2>19 - S</h2>
            </div>
            <div class="right-text" style="flex: 1; text-align: right;">
                <h3>{time_19S} mins</h3>
            </div>
            </div>
            <div class="card" style="width: 90%; padding: 20px; border: 3px solid #000; border-radius: 3px; margin: 10px; display: flex; flex-direction: row; justify-content: space-between;align-items: center;">
            <div class="left-text" stlye ="flex: 1;">
                <h2>7 - S</h2>
            </div>
            <div class="right-text" style="flex: 1; text-align: right;">
                <h3>{time_7S} mins</h3>
            </div>
            </div>
            <div class="card" style="width: 90%; padding: 20px; border: 3px solid #000; border-radius: 3px; margin: 10px; display: flex; flex-direction: row; justify-content: space-between;align-items: center;">
            <div class="left-text" stlye ="flex: 1;">
                <h2>301 - S</h2>
            </div>
            <div class="right-text" style="flex: 1; text-align: right;">
                <h3>{time_301S} mins</h3>
            </div>
            </div>
            <div class="card" style="width: 90%; padding: 20px; border: 3px solid #000; border-radius: 3px; margin: 10px; display: flex; flex-direction: row; justify-content: space-between;align-items: center;">
            <div class="left-text" stlye ="flex: 1;">
                <h2>301 - N</h2>
            </div>
            <div class="right-text" style="flex: 1; text-align: right;">
                <h3>{time_301N} mins</h3>
            </div>
            </div>
            
        </body>
        </html>
        """
        # Read and send the HTML file with dynamic data
        # with open('index.html', 'w') as f:
        #     f.write(html_content)
        self.wfile.write(html_content.encode())
        return
        # else:
        #     return SimpleHTTPRequestHandler.do_GET(self)

# PORT = 8000

# with TCPServer(("", PORT), MyHandler) as httpd:
#     print(f"Serving on port {PORT}")
#     httpd.serve_forever()


#filtered_df = stop_times_df[stop_times_df['stop_id'] == 1171]

# Print the filtered DataFrame
#print(filtered_stop_times)



#print(bus_route_id)
