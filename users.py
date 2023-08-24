
from flask_sqlalchemy import SQLAlchemy
from app import app
# from socket_worker import update_users
db = SQLAlchemy(app)
class User(db.Model):
    """ Create user table"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean, unique=False,default=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.admin = False

def test_admin():
    with app.app_context():
        data = User.query.filter_by(username="admin").first()
        if data is None:
            default_admin = User(
                username="admin",
                password="admin")
            db.session.add(default_admin)
            db.session.commit()
            data = User.query.filter_by(username="admin").first()
            data.admin = True
            db.session.commit()
            print("Created default admin user account")
        # print(data)
        # else:
        #     print(data.admin)
