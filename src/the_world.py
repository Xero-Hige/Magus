import re

from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

from libs.locations import get_coordinates_from_code
from map_grid import MapGrid

COLUMNS = 100
ROWS = 200

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['GOOGLEMAPS_KEY'] = ""

GoogleMaps(app)

EMOJIS = re.compile(u"\\ud83d", flags=re.UNICODE)

W, S, E, N = get_coordinates_from_code("AR")
GRID = MapGrid(north=N, south=S, east=E, west=W, grid_rows=200, grid_columns=100)


@app.route('/', methods=["GET"])
def map_show():
    rectangles = GRID.get_status()
    map = Map(
            identifier="rectmap",
            varname="rectmap",
            lat=(S + N) / 2,
            lng=(W + E) / 2,
            rectangles=rectangles,
            style="height:600px;width:800px;margin:0;",
            zoom=7
    )

    return render_template("map.html", map=map)
