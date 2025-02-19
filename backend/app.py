from flask import Flask, render_template
from flask_cors import CORS
from routes.api_v2 import api_v2
import argparse
from config.socketio_instance import socketio

app = Flask(__name__)
CORS(app)
socketio.init_app(app)

app.register_blueprint(api_v2)

argparser = argparse.ArgumentParser()

argparser.add_argument("-p", "--port", default=5000, type=int, help="Port to run the server on.")
argparser.add_argument("-d", "--debug", default=False, type=bool, help="Enable debug mode.")
argparser.add_argument("-H", "--host", default="0.0.0.0", type=str, help="Host to run the server on.")

args = argparser.parse_args()

port = args.port
debug = args.debug
host = args.host

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")
    
if __name__ == "__main__":
    socketio.run(host=host, port=port, debug=debug)