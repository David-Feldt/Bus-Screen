import datetime

import requests
import zipfile
import pandas as pd
from io import BytesIO

from http.server import SimpleHTTPRequestHandler
from http.server import BaseHTTPRequestHandler

from socketserver import TCPServer
from apscheduler.schedulers.background import BackgroundScheduler


def update_data():
    global filtered_stop_times_201W, filtered_stop_times_19S, filtered_stop_times_7S, filtered_stop_times_201E, filtered_stop_times_301S, filtered_stop_times_301N
    # Download the file
    response = requests.get('https://www.regionofwaterloo.ca/opendatadownloads/GRT_GTFS.zip')
    z = zipfile.ZipFile(BytesIO(response.content))
    #z = zipfile.ZipFile('./GRT_GTFS.zip','r')
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
    #print("Date of interest",date_of_interest)
    filtered_calendar_dates = calendar_dates_df[calendar_dates_df['date'] == date_of_interest]
    service_ids = filtered_calendar_dates['service_id'].unique()
    #print("Service id",service_ids)

    #  ONLY HAVE WITH CORRECT SERVIE_ID
    filtered_trips_201W = trip_df[((trip_df['route_id'] == bus_route_id_201) | (trip_df['route_id'] == bus_route_id_31)) & (trip_df['direction_id'] == 0) & (trip_df['service_id'].isin(service_ids))]
    filtered_trips_19N = trip_df[(trip_df['route_id'] == bus_route_id_19) & (trip_df['direction_id'] == 0) & (trip_df['service_id'].isin(service_ids))]
    filtered_trips_19S = trip_df[(trip_df['route_id'] == bus_route_id_19) & (trip_df['direction_id'] == 1) & (trip_df['service_id'].isin(service_ids))]
    filtered_trips_7N = trip_df[(trip_df['route_id'] == bus_route_id_7) & (trip_df['direction_id'] == 0) & (trip_df['service_id'].isin(service_ids))]
    filtered_trips_7S = trip_df[(trip_df['route_id'] == bus_route_id_7) & (trip_df['direction_id'] == 1) & (trip_df['service_id'].isin(service_ids))]
    filtered_trips_201E = trip_df[((trip_df['route_id'] == bus_route_id_201) | (trip_df['route_id'] == bus_route_id_31)) & (trip_df['direction_id'] == 1) & (trip_df['service_id'].isin(service_ids))]
    filtered_trips_301N = trip_df[(trip_df['route_id'] == bus_route_id_301) & (trip_df['direction_id'] == 0) & trip_df['service_id'].isin(service_ids)]
    filtered_trips_301S = trip_df[(trip_df['route_id'] == bus_route_id_301) & (trip_df['direction_id'] == 1) & trip_df['service_id'].isin(service_ids)]
    #print(bus_trips.head())

    #print("Filtered trips",filtered_trips_301N)
    stop_times_df = dfs[filenames.index('stop_times.txt')]
    stops_df = dfs[filenames.index('stops.txt')]

    stop_name = 'Hazel / Columbia'
    stop_idS = 3623
    stop_idN = 1171
    stop_idE =  2512
    stop_idW = 2524
    stop_id7N = 1915 #2509 #4073
    stop_id7S = 2509
    stop_id301S = 6004
    stop_id301N = 6120

    trip_ids_201W = filtered_trips_201W['trip_id']
    trip_ids_19S = filtered_trips_19S['trip_id']
    trip_ids_19N = filtered_trips_19N['trip_id']
    trip_ids_7S = filtered_trips_7S['trip_id']
    trip_ids_7N = filtered_trips_7N['trip_id']
    trip_ids_201E = filtered_trips_201E['trip_id']
    trip_ids_301N = filtered_trips_301N['trip_id']
    trip_ids_301S = filtered_trips_301S['trip_id']

    #print(type(trip_ids))
    # Filter the stop_times_df DataFrame based on trip_id
    filtered_stop_times_201W = stop_times_df[stop_times_df['trip_id'].isin(trip_ids_201W)]
    filtered_stop_times_19S = stop_times_df[stop_times_df['trip_id'].isin(trip_ids_19S)]
    filtered_stop_times_19N = stop_times_df[stop_times_df['trip_id'].isin(trip_ids_19N)]
    filtered_stop_times_7S = stop_times_df[stop_times_df['trip_id'].isin(trip_ids_7S)]
    filtered_stop_times_7N = stop_times_df[stop_times_df['trip_id'].isin(trip_ids_7N)]
    filtered_stop_times_201E = stop_times_df[stop_times_df['trip_id'].isin(trip_ids_201E)]
    filtered_stop_times_301S = stop_times_df[stop_times_df['trip_id'].isin(trip_ids_301S)]
    filtered_stop_times_301N = stop_times_df[stop_times_df['trip_id'].isin(trip_ids_301N)]


    stop_ids_201W = filtered_stop_times_201W['stop_id']
    stop_ids_19S = filtered_stop_times_19S['stop_id']
    stop_ids_19N = filtered_stop_times_19N['stop_id']
    stop_ids_7S = filtered_stop_times_7S['stop_id']
    stop_ids_7N = filtered_stop_times_7N['stop_id']
    stop_ids_201E = filtered_stop_times_201E['stop_id']
    stop_ids_301S = filtered_stop_times_301S['stop_id']
    stop_ids_301N = filtered_stop_times_301N['stop_id']

    filtered_stop_times_201W = filtered_stop_times_201W[filtered_stop_times_201W['stop_id'] == stop_idW]
    filtered_stop_times_19S = filtered_stop_times_19S[filtered_stop_times_19S['stop_id'] == stop_idS]
    filtered_stop_times_19N = filtered_stop_times_19N[filtered_stop_times_19N['stop_id'] == stop_idN]
    filtered_stop_times_201E = filtered_stop_times_201E[filtered_stop_times_201E['stop_id'] == stop_idE]
    filtered_stop_times_7S = filtered_stop_times_7S[filtered_stop_times_7S['stop_id'] == stop_id7S]
    filtered_stop_times_7N = filtered_stop_times_7N[filtered_stop_times_7N['stop_id'] == stop_id7N]
    filtered_stop_times_301S = filtered_stop_times_301S[filtered_stop_times_301S['stop_id'] == stop_id301S]
    filtered_stop_times_301N = filtered_stop_times_301N[filtered_stop_times_301N['stop_id'] == stop_id301N]

    #print(filtered_stop_times['arrival_time'])
    #filtered_stop_times_301N.to_csv('stop_times_301N.csv', index=False)

    filtered_stop_times_201W['arrival_time'] = filtered_stop_times_201W['arrival_time'].str.replace('^24', '00')
    filtered_stop_times_201E['arrival_time'] = filtered_stop_times_201E['arrival_time'].str.replace('^24', '00')
    filtered_stop_times_19S['arrival_time'] = filtered_stop_times_19S['arrival_time'].str.replace('^24', '00')
    filtered_stop_times_7S['arrival_time'] = filtered_stop_times_7S['arrival_time'].str.replace('^24', '00')
    filtered_stop_times_301N['arrival_time'] = filtered_stop_times_301N['arrival_time'].str.replace('^24', '00')
    filtered_stop_times_301S['arrival_time'] = filtered_stop_times_301S['arrival_time'].str.replace('^24', '00')

    filtered_stop_times_201W['arrival_time'] = pd.to_datetime(filtered_stop_times_201W['arrival_time']).dt.time
    filtered_stop_times_201E['arrival_time'] = pd.to_datetime(filtered_stop_times_201E['arrival_time']).dt.time
    filtered_stop_times_19S['arrival_time'] = pd.to_datetime(filtered_stop_times_19S['arrival_time']).dt.time
    filtered_stop_times_7S['arrival_time'] = pd.to_datetime(filtered_stop_times_7S['arrival_time']).dt.time
    filtered_stop_times_301S['arrival_time'] = pd.to_datetime(filtered_stop_times_301S['arrival_time']).dt.time
    filtered_stop_times_301N['arrival_time'] = pd.to_datetime(filtered_stop_times_301N['arrival_time']).dt.time

# Create a scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(update_data, 'interval', hours=1)
scheduler.start()

# Update the data immediately
update_data()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
    #if self.path == '/':
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Get dynamic data from Python
        now = datetime.datetime.now().time()
        date =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        next_bus_time_201E = filtered_stop_times_201E[filtered_stop_times_201E['arrival_time'] > now]['arrival_time'].min()
        next_bus_time_19S = filtered_stop_times_19S[filtered_stop_times_19S['arrival_time'] > now]['arrival_time'].min()
        next_bus_time_7S = filtered_stop_times_7S[filtered_stop_times_7S['arrival_time'] > now]['arrival_time'].min()
        next_bus_time_301S = filtered_stop_times_301S[filtered_stop_times_301S['arrival_time'] > now]['arrival_time'].min()
        next_bus_time_301N = filtered_stop_times_301N[filtered_stop_times_301N['arrival_time'] > now]['arrival_time'].min()
        
        time_7S = datetime.datetime.combine(datetime.date.today(), next_bus_time_7S) - datetime.datetime.combine(datetime.date.today(), now)
        time_201E = datetime.datetime.combine(datetime.date.today(), next_bus_time_201E) - datetime.datetime.combine(datetime.date.today(), now)
        time_19S = datetime.datetime.combine(datetime.date.today(), next_bus_time_19S) - datetime.datetime.combine(datetime.date.today(), now)
        time_301N = datetime.datetime.combine(datetime.date.today(), next_bus_time_301N) - datetime.datetime.combine(datetime.date.today(), now)
        time_301S = datetime.datetime.combine(datetime.date.today(), next_bus_time_301S) - datetime.datetime.combine(datetime.date.today(), now)
        time_7S = int(time_7S.total_seconds() // 60)
        time_201E = int(time_201E.total_seconds() // 60)
        time_19S = int(time_19S.total_seconds() // 60)
        time_301N = int(time_301N.total_seconds() // 60)
        time_301S = int(time_301S.total_seconds() // 60)
        html_content = f"""
        <!DOCTYPE html>
        <html lang='en'>
        <head>
            <title>Next Bus</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="refresh" content="5">
        </head>
        <body>
            <div class="container">
             <h3>{date}</h3>
    <!-- Bus 101 -->
    <div class="bus-row">
        <div class="bus-info">
            <div class="bus-number">201E</div>
            <div class="bus-details">
                <div class="bus-route">201 - East</div>
            </div>
        </div>
        <div class="bus-time">
            <div class="arrival-time">
                <span class="minutes">{time_201E}</span> min
            </div>
        </div>
    </div>
    <div class="bus-row">
        <div class="bus-info">
            <div class="bus-number">19S</div>
            <div class="bus-details">
                <div class="bus-route">19 - South</div>
            </div>
        </div>
        <div class="bus-time">
            <div class="arrival-time">
                <span class="minutes">{time_19S}</span> min
            </div>
        </div>
    </div>
    <div class="bus-row">
        <div class="bus-info">
            <div class="bus-number">7S</div>
            <div class="bus-details">
                <div class="bus-route">7 - South</div>
            </div>
        </div>
        <div class="bus-time">
            <div class="arrival-time">
                <span class="minutes">{time_7S}</span> min
            </div>
        </div>
    </div>
    <div class="bus-row">
        <div class="bus-info">
            <div class="bus-number-ion">301S</div>
            <div class="bus-details">
                <div class="bus-route">301 Ion - South</div>
            </div>
        </div>
        <div class="bus-time">
            <div class="arrival-time">
                <span class="minutes">{time_301S}</span> min
            </div>
        </div>
    </div>
    <div class="bus-row">
        <div class="bus-info">
            <div class="bus-number-ion">301N</div>
            <div class="bus-details">
                <div class="bus-route">301 Ion - North</div>
            </div>
        </div>
        <div class="bus-time">
            <div class="arrival-time">
                <span class="minutes">{time_301N}</span> min
            </div>
        </div>
    </div>
 
    <!-- Additional rows can be added here -->
</div>

<style>
    .container {{
        font-family: Arial, sans-serif;
        background-color: #fff;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .bus-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        padding: 10px;
        background: #f7f7f7;
        border-radius: 5px;
    }}
    .bus-info {{
        display: flex;
        align-items: center;
    }}
    .bus-number {{
        background-color: #8dc63f;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }}
    .bus-number-ion {{
        background-color: #3f4ac6;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }}
    .bus-details {{
        margin-left: 10px;
    }}
    .bus-route {{
        font-weight: bold;
    }}
    .bus-time {{
        display: flex;
        align-items: center;
        flex-direction: column;
        text-align: right;
    }}
    .arrival-time {{
        font-weight: bold;
        font-size: 1.5em;
    }}
    .minutes {{
        font-size: 2em;
    }}
</style>
            
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

PORT = 8000

# with TCPServer(("", PORT), handler) as httpd:
#     print(f"Serving on port {PORT}")
#     httpd.serve_forever()


#filtered_df = stop_times_df[stop_times_df['stop_id'] == 1171]

# Print the filtered DataFrame
#print(filtered_stop_times)



#print(bus_route_id)
