
from flask import url_for, render_template, request, redirect, session

# from instagram import get_followed_by, get_user_name
from app import app
from users import User, db, test_admin

    # default_admin = User(
    #     username="admin",
    #     password="admin")


@app.route('/', methods=['GET', 'POST'])
def home():
    """ Session control"""
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        if request.method == 'POST':
            username = get_user_name(request.form['username'])
            return render_template('index.html', data=get_followed_by(username))
        return render_template('index.html')

@app.route('/users', methods=['GET', 'POST'])
def users():
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
            new_user = User(
                username=request.form['username'],
                password=request.form['password'])
            db.session.add(new_user)
            db.session.commit()
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
    app.run(host='0.0.0.0')

