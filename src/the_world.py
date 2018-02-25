from flask import Flask, render_template

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/', methods=["GET"])
def map_show():
    return render_template("map.html",
                           subscribe_key="sub-c-1d2d27fc-12bd-11e8-91c1-eac6831c625c",
                           publish_key="pub-c-7a828306-4ddf-425c-80ec-1e4f8763c088",
                           map_access_token="pk.eyJ1IjoieGVyby1oaWdlIiwiYSI6ImNqZG9zZ2dsZjFlMmUycW80Zm5rNmk0cXgifQ.vCOrMcBB5WsK2SW2XrS_Qw",
                           buffer_max_size=250000)
