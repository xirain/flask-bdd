# flaskr.py

from flask import Flask, request, session, redirect, render_template, flash, url_for, g, abort
import sqlite3
import os
#####
#####CONFIG
DATABASE = 'flaskr.db'
USERNAME='admin'
PASSWORD='admin'
SECRET_KEY='/+*k\x82\x05\xb7\x188\xbfl\xd5\x8d\xb2,F\x9c\xc2\x9b\xa0cu\xaf\xa5'

DATABASE_PATH = os.path.join(os.path.abspath(os.curdir),DATABASE)

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login/authentication/session management."""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))

    return render_template('login.html', error=error)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)

    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)', [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """User logout/authentication/session management."""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))

def connect_db():
    """Connects to the database."""
    rv = sqlite3.connect(app.config['DATABASE_PATH'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

   
@app.route('/')
def index():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('index.html', entries=entries)


if __name__ == '__main__':
    app.run(debug=True)