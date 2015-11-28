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


@app.route('/display')
def print_users():
    db = get_db()
    cur = db.execute('SELECT username FROM user ORDER BY id ASC')
    entries = [dict(username=row[0]) for row in cur.fetchall()]
    return render_template('displayUsers.html',entries=entries)

@app.route('/feed')
def feed():
    db = get_db()
    cur = db.execute('SELECT title,Uid,loc,post FROM post ORDER BY id DESC')
    posts = [dict(title=row[0],Uid=row[1],loc=row[2],post=row[3]) for row in cur.fetchall()]
    return render_template('feed.html',posts=posts)

@app.route('/add',methods=['GET','POST'])
def add():
    if request.method == 'GET':
        return render_template ('createAccount.html')
    if request.method == 'POST':
      error = []
      username = request.form['username']
      form = request.form
      db= get_db()
      VAR= "SELECT username FROM user WHERE username LIKE '"+str(username)+ "'"
      Fname = db.cursor().execute(VAR)
      print Fname
      cur =[dict(username=row[0]) for row in Fname.fetchall()]
      database= str(cur)
      if username in  database:
          error = "username already in use"
          return render_template('createAccount.html',error=error)
      if request.form['password'] != request.form["confirm_password"]:
          error.append("please enter same password")
      if not error:
          #insert in db
          db.cursor().execute('INSERT INTO user (username,password) values(?,?)',[request.form['username'],request.form['password']])
          db.commit()
          error="Account Created"
      return render_template('createAccount.html', error = error )
      return render_template('createAccount.html', error=error)


@app.route('/post', methods=['GET', 'POST'])
def post():
     if Session() is None:
       return redirect (url_for('login'))
     else:
      if request.method == 'GET':
        return render_template('newpost.html')
      if request.method == 'POST':
       info = []
       db = get_db()
       db.cursor().execute('INSERT INTO post (Uid,title,post,loc) VALUES(?,?,?,?)',[session['username'],request.form['title'],request.form['post'],request.form['location']])
       db.commit()
       info.append("new post added")
       return render_template('newpost.html', info = info )
    
      


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

def Session():
  if 'username' in session:
   return session
  else:
   return None

@app.route("/", methods={"GET","POST"})
def profile():
  if Session() is None:
    return redirect(url_for('login'))
    print "not logged in"
  else: 
   print "logged in"
   db = get_db()
   cur = db.execute("SELECT title,Uid,loc,post FROM post WHERE Uid LIKE '" + session['username'] +"'")
   posts = [dict(title=row[0],Uid=row[1],loc=row[2],post=row[3])for row in cur.fetchall()]
   return render_template('home.html',posts=posts)

if __name__ == "__main__":
  app.run(host='0.0.0.0',debug=True)


