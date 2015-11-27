from flask import Flask, redirect, url_for, abort, request, render_template, session, g, flash
import sqlite3, os , Cookie
import ConfigParser
from flask.ext.wtf import Form
from wtforms import TextField, HiddenField
from contextlib import closing
#from flask.ext.bcrypt import Bcrypt

#app create
app = Flask(__name__)
db_location = 'VAR/data.db'
secret_key = 'the secret key'
app.secret_key = 'secret'
#bcrypt = Bcrypt(app)
#database functions


def get_db():
    db = getattr(g,'db',None)
    if db is None:
      db =sqlite3.connect(db_location)
      g.db = db
      db.row_factory = sqlite3.Row
      return db

@app.teardown_request
def teardown_request(exception):
  db = getattr(g,'db', None)
  if db is not None:
    db.close

def init_db():
  with app.app_context():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit

#def query_db(query, arg=(), one=False):
#    db = get_db()
#    cur = db.execute(query,args)
#    rv = [dict((cur.description[idx][0], value) for idx, value in enumerate(row)) for row in cur.fetchall()]
#    return (rv[0] if rv else None) if one else rv

@app.route('/display')
def print_users():
    db = get_db()
    cur = db.execute('SELECT username,password FROM user ORDER BY id ASC')
    entries = [dict(username=row[0],password=row[1]) for row in cur.fetchall()]
    return render_template('displayUsers.html',entries=entries)

@app.route('/feed')
def feed():
    db = get_db()
    cur = db.execute('SELECT title,post FROM post ORDER BY id ASC')
    posts = [dict(title=row[0],post=row[1]) for row in cur.fetchall()]
    return render_template('feed.html',posts=posts)

@app.route('/add',methods=['GET','POST'])
def add():
    if request.method == 'GET':
        return render_template ('createAccount.html')
    if request.method == 'POST':
      error = []
      form = request.form
      if request.form['password'] != request.form["confirm_password"]:
          error.append("please enter same password")
      if not error:
          db = get_db()
          #insert in db
          db.cursor().execute('INSERT INTO user (username,password) values(?,?)',[request.form['username'],request.form['password']])
          db.commit()
          error.append("yeahh info added")
      return render_template('createAccount.html', error = error, form = form )
      return render_template('createAccount.html', error=error)


@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == 'GET':
        return render_template ('newpost.html')
    if request.method == 'POST':
      info = []
      form = request.form
      db = get_db()
      db.cursor().execute('INSERT INTO post (title,post) values(?,?)',[request.form['title'],request.form['post']])
      db.commit()
      info.append("post added")
    return render_template('newpost.html', info = info , form = form)


@app.route('/login', methods = ['GET','POST'])
def login():
  if request.method == 'POST':
    db = get_db()
    username = request.form['username']
    password = request.form['password']
    VAR1 = "SELECT password FROM user WHERE username LIKE '" + str(username) + "'"
    VAR2 = "SELECT id  FROM user WHERE username LIKE '" + str(username) + "'"
    print "sql "  + VAR2
    SU = db.cursor().execute(VAR1)
    SI = db.cursor().execute(VAR2)
    print SI
    cur = [dict(password=row[0]) for row in SU.fetchall()]
    cur2 = [dict(id=row[0]) for row in SI.fetchall()]
    print cur2
    sId = str(cur2)
    info = str(cur)
    print info
    print sId
    SID = sId.replace("[{'id': ","").replace("}]","")
    print SID
    print password
    password = str(password)
    if password in info:
      print "success"
      session['id'] = SID
      session['username']= username
      info = "You have been logged in."
      return redirect(url_for('profile'))
    else:
      info = "Wrong information please try again"
      return render_template('login.html', info=info)
  else:
    info = "Please login"
    return render_template('login.html', info=info)

@app.route('/logout')
def logout():
    session.pop('username',None)
    session.pop('id',None)
    print" logged out"
    return redirect(url_for('login'))



@app.route("/", methods={"GET","POST"})
def profile():
 if 'username' in session:
   print"lol "
 return render_template('home.html')

if __name__ == "__main__":
  app.run(host='0.0.0.0',debug=True)


