
from flask import url_for, render_template, request, redirect, session

from users import User, db, test_admin
from socket_worker import socketapp, app, create_user




@app.route('/')
def home():
    global test
    test = ["a", "b", "c"]
    """ Session control"""
    return render_template('index.html')

@app.route('/users', methods=['GET', 'POST'])
def users():
    global test
    if session['logged_in']:
        if request.method == 'GET':
            return render_template('users.html')
        else:
            pass
            #handle user data here
    else:
        return 'Unauthorized', 503


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Form"""
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name = request.form['username']
        passw = request.form['password']
        try:
            data = User.query.filter_by(username=name, password=passw).first()
            if data is not None:
                session['logged_in'] = True
                session['admin'] = data.admin
                session['username'] = data.username
                return redirect(url_for('home'))
            else:
                return 'Dont Login'
        except:
            return "Dont Login"


@app.route('/register/', methods=['GET', 'POST'])
def register():
    """Register Form"""
    if request.method == 'POST':
        data = User.query.filter_by(username=request.form['username']).first()
        if data is not None:
            return render_template('register.html', userExists=True)
        else:
            create_user(request.form['username'], request.form['password'])
            return render_template('login.html')
    return render_template('register.html')


@app.route("/logout")
def logout():
    """Logout Form"""
    session['logged_in'] = False
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.app_context().push()
    app.debug = True
    db.create_all()
    test_admin()
    app.secret_key = "123"
    socketapp.run(app, host="0.0.0.0")



# @socketio.on('my event')
# def handle_my_custom_event(json):
#     print('received json: ' + str(json))

# @socketapp.on('connect')
# def connect_handler():
#     print("asdf")
#     if session['current_user'].is_authenticated:
#         print("gotem")
#     else:
#         print("boo")
#         return False