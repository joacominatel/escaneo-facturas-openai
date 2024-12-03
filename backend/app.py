from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from routes.api import api

app = Flask(__name__)
CORS(app)

app.register_blueprint(api)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)