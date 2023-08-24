
from flask import url_for, render_template, request, redirect, session
import functools
from users import User, db, test_admin
from socket_worker import socketapp, app, create_user, reset_password_for_user
from queue_worker import add_to_queue, new_request

def admin_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if session and session['logged_in'] and session['admin']:
            return f(*args, **kwargs)
        else:
            return 'Unauthorized', 503
    return wrapped

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if session and session['logged_in']:
            return f(*args, **kwargs)
        else:
            return 'Unauthorized', 503
    return wrapped

@app.route('/')
def home():
    """ Session control"""
    if "req" in request.args.keys() and request.args['req'] == "true":
        return render_template('index.html', newsong=True)
    return render_template('index.html', newsong=False)

@app.route('/reset-password', methods=['GET', 'POST'])
@authenticated_only
def reset_password():
    if request.method == 'GET':
        if "user" in request.args.keys():
            if not session['admin']:
                return 'Unauthorized', 503
            return render_template("reset-admin.html",username=request.args['user'])
        else:
            return render_template("reset-password.html")
    else:
        if request.form and 'newPassword' in request.form.keys() and 'curPassword' in request.form.keys() and 'confirmPassword' in request.form.keys():
            if request.form['confirmPassword'] == request.form['newPassword']:
                data = User.query.filter_by(username=session['username'], password=request.form['curPassword']).first()
                if data is not None:
                    reset_password_for_user(session['username'], request.form['newPassword'])
                    return redirect(url_for('home'))
                else:
                    return render_template('reset-password.html', passwordIncorrect=True)
            else:
                return render_template('reset-password.html', passwordNotMatch=True)
        elif 'username' in request.form.keys() and 'newPassword' in request.form.keys():
                if session['admin']:
                    reset_password_for_user(request.form['username'], request.form['newPassword'])
                    return redirect(url_for('home'))
                else:
                    return 'Unauthorized', 503
        else:
            print(request.form.keys())
            return render_template('reset-password.html')
    return render_template('reset-password.html')

@app.route('/users')
@admin_only
def users():
    return render_template('users.html')
@app.route('/queue')
@authenticated_only
def queue():
    if session['admin']:
        return render_template('queue-admin.html')
    else:
        return render_template('queue.html')

@app.route('/request', methods=['GET', 'POST'])
@authenticated_only
def requestsong():
    if request.method == 'GET':
        return render_template('request.html')
    else:
        username = session['username']
        if not request.form['song'] or not request.form['author']:
            return render_template('request.html')
        song = request.form['song']
        author = request.form['author']
        req = new_request(username, song, author)
        add_to_queue(req)
        session['request'] = True
        return redirect(url_for('home') + "?req=true")


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
                return render_template('login.html', incorrect=True)
        except:
            return "Error"


@app.route('/register/', methods=['GET', 'POST'])
def register():
    """Register Form"""
    print(request)
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