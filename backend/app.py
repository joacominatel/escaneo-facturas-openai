from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from routes.api import api

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(api)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)