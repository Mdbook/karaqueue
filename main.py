from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import users
db = users.db
def init():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    users.db.init_app(app)

    # blueprint for auth routes in our app
    # from .auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    # from .main import main as main_blueprint
    # app.register_blueprint(main_blueprint)

    return app

app = init()

@app.route("/")
def index(name=None):
    return render_template('index.html', name=name)
app.run(host="0.0.0.0")