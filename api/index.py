import datetime
import zipfile
from http.server import BaseHTTPRequestHandler
from io import BytesIO

import pandas as pd
import pytz
import requests
from apscheduler.schedulers.background import BackgroundScheduler

GTFS_URL = 'https://www.regionofwaterloo.ca/opendatadownloads/GRT_GTFS.zip'
TIMEZONE = pytz.timezone('America/New_York')

# Each row on the screen: which routes, which direction, and which stop to watch.
# direction_id comes from trips.txt (0/1); stop_id comes from stops.txt.
BUSES = [
    {'label': '201E', 'name': '201 - East',      'routes': [201, 31], 'direction': 1, 'stop_id': 2512, 'ion': False},
    {'label': '19S',  'name': '19 - South',      'routes': [19],      'direction': 1, 'stop_id': 3623, 'ion': False},
    {'label': '7S',   'name': '7 - South',       'routes': [7],       'direction': 1, 'stop_id': 2509, 'ion': False},
    {'label': '301S', 'name': '301 Ion - South', 'routes': [301],     'direction': 1, 'stop_id': 6004, 'ion': True},
    {'label': '301N', 'name': '301 Ion - North', 'routes': [301],     'direction': 0, 'stop_id': 6120, 'ion': True},
]

# label -> sorted list of datetime.time arrivals for today
arrivals = {}


def to_time(gtfs_time):
    # GTFS allows hours >= 24 for trips that run past midnight
    h, m, s = (int(x) for x in gtfs_time.split(':'))
    return datetime.time(h % 24, m, s)


def update_data():
    response = requests.get(GTFS_URL)
    z = zipfile.ZipFile(BytesIO(response.content))
    trips = pd.read_csv(z.open('trips.txt'))
    stop_times = pd.read_csv(z.open('stop_times.txt'))
    calendar_dates = pd.read_csv(z.open('calendar_dates.txt'))

    today = int(datetime.datetime.now(TIMEZONE).strftime('%Y%m%d'))
    service_ids = calendar_dates[calendar_dates['date'] == today]['service_id'].unique()
    trips = trips[trips['service_id'].isin(service_ids)]

    for bus in BUSES:
        trip_ids = trips[trips['route_id'].isin(bus['routes']) & (trips['direction_id'] == bus['direction'])]['trip_id']
        times = stop_times[stop_times['trip_id'].isin(trip_ids) & (stop_times['stop_id'] == bus['stop_id'])]['arrival_time']
        arrivals[bus['label']] = sorted(to_time(t) for t in times)


def minutes_until_next(label, now):
    upcoming = [t for t in arrivals.get(label, []) if t > now]
    if not upcoming:
        return '--'
    today = datetime.date.today()
    delta = datetime.datetime.combine(today, upcoming[0]) - datetime.datetime.combine(today, now)
    return int(delta.total_seconds() // 60)


# Refresh the schedule every hour so the service day stays current
scheduler = BackgroundScheduler()
scheduler.add_job(update_data, 'interval', hours=1)
scheduler.start()

update_data()


ROW_TEMPLATE = """
    <div class="bus-row">
        <div class="bus-info">
            <div class="{badge}">{label}</div>
            <div class="bus-details">
                <div class="bus-route">{name}</div>
            </div>
        </div>
        <div class="bus-time">
            <div class="arrival-time">
                <span class="minutes">{minutes}</span> min
            </div>
        </div>
    </div>"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Next Bus</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="5">
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
        .bus-number, .bus-number-ion {{
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
        }}
        .bus-number {{ background-color: #8dc63f; }}
        .bus-number-ion {{ background-color: #3f4ac6; }}
        .bus-details {{ margin-left: 10px; }}
        .bus-route {{ font-weight: bold; }}
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
        .minutes {{ font-size: 2em; }}
    </style>
</head>
<body>
    <div class="container">
        <h3>{date}</h3>{rows}
    </div>
</body>
</html>
"""


def render_page():
    now = datetime.datetime.now(TIMEZONE)
    rows = ''.join(
        ROW_TEMPLATE.format(
            badge='bus-number-ion' if bus['ion'] else 'bus-number',
            label=bus['label'],
            name=bus['name'],
            minutes=minutes_until_next(bus['label'], now.time()),
        )
        for bus in BUSES
    )
    return PAGE_TEMPLATE.format(date=now.strftime('%Y-%m-%d %H:%M:%S'), rows=rows)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(render_page().encode())
