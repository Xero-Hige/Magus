import re

from flask import Flask

from map_grid import MapGrid

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

EMOJIS = re.compile(u"\\ud83d", flags=re.UNICODE)

GRIDS = {}


@app.route('/', methods=["GET"])
def map_show():
    GRIDS[0] = MapGrid()
