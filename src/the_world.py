import os

from flask import Flask, render_template

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/', methods=["GET"])
def map_show():
    return render_template("map.html",
                           Title="The World",
                           subscribe_key=os.environ["PUBNUB_SUB_KEY"],
                           publish_key=os.environ["PUBNUB_PUB_KEY"],
                           map_access_token=os.environ["MAPBOX_KEY"],
                           buffer_max_size=os.environ["BUFFER_SIZE"])
