from flask import Flask, render_template
from flask_cors import CORS
import requests

app = Flask(__name__,
            static_folder="./dist/static",
            template_folder="./dist")

cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/')
def Home():
    return render_template("index.html")


# @app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return requests.get('http://localhost:8080/{}'.format(path)).text
    return render_template("index.html")
