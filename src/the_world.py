import re

from flask import Flask, render_template
from flask_googlemaps import GoogleMaps

from libs.locations import get_coordinates_from_code

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
    return render_template("map.html", lat=(S + N) / 2, long=(W + E) / 2)
