from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "<p>Welcome to KaraQueue!</p>"
app.run(host="0.0.0.0")