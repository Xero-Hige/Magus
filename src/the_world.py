import random
import re

from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

from gmaps_rectangle import GmapsRectangle
from grid_region import GridRegion
from libs.locations import get_coordinates_from_code

COLUMNS = 100
ROWS = 200

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['GOOGLEMAPS_KEY'] = ""

GoogleMaps(app)

EMOJIS = re.compile(u"\\ud83d", flags=re.UNICODE)

GRIDS = {}


@app.route('/', methods=["GET"])
def map_show():
    # GRIDS[0] = MapGrid()
    W, S, E, N = get_coordinates_from_code("AR")

    rectangles = []
    row_size = (S - N) / ROWS
    col_size = (W - E) / COLUMNS

    for row in range(ROWS):
        for column in range(COLUMNS):
            north = N + row_size * row
            south = N + row_size * (row + 1)
            east = E + col_size * column
            west = E + col_size * (column + 1)
            rect = GmapsRectangle(north=north, south=south, west=west, east=east)
            rect.set_colors(random.choice([GridRegion.SAD, GridRegion.HAPPY, GridRegion.INDIFERENT, GridRegion.ANGRY]),
                            random.choice([0.3, 0.5, 0.8, 1]))
            rectangles.append(rect.get_renderable_info())

    map = Map(
            identifier="rectmap",
            varname="rectmap",
            lat=(S + N) / 2,
            lng=(W + E) / 2,
            rectangles=rectangles,
            style="height:600px;width:800px;margin:0;"
    )

    return render_template("map.html", map=map)
