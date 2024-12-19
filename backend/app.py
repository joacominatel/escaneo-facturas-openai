from flask import Flask, render_template
from flask_cors import CORS
from routes.api_v2 import api_v2

app = Flask(__name__)
CORS(app, resources={r"/api_v2/*": {"origins": "*"}})

app.register_blueprint(api_v2)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")
    
if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")