from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from datetime import datetime
import os

app = Flask('app')
app.debug = True
app.secret_key = "Books"

try:
  app.config["MONGO_URI"] = "mongodb://bookbounce:jaimadurga@cluster0-shard-00-00.y2efj.mongodb.net:27017,cluster0-shard-00-01.y2efj.mongodb.net:27017,cluster0-shard-00-02.y2efj.mongodb.net:27017/books?ssl=true&replicaSet=atlas-2si8y7-shard-0&authSource=admin&retryWrites=true&w=majority"
  mongo = PyMongo(app)
  print("connected!")
except:
  print("Cannot connect")

@app.route('/', methods=['GET', 'POST'])
def home():
  return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'GET':
    session.pop('username', None)
    print("User logged out")
    return render_template("login.html")
  else:
    email = request.form.get('email')
    password = request.form.get('password')
    db_info = mongo.db.user.find({})
    success = False
    for user in db_info: 
      if (email == user["email"] and password == user["p"]):
        success = True 
        print("passed")
        session['username'] = user["username"]
        print(session['username'])
        return redirect(url_for('viewListing', user=user["username"]))
    else:
      print("failed")
      message = "Invalid credentials"
      return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'GET':
    return render_template('register.html')
  else:
    name = request.form.get('name')
    username = request.form.get('username')
    email = request.form.get('email')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    email_db = mongo.db.user.find({})
    success = True
    
    for user in email_db:
      if email == user["email"]:
        message = "Email already exists. Please try again."
        print(message)
        success = False
        return redirect(url_for('register'))
      elif username == user["username"]:
        message = "Username already exists. Please try again."
        print(message)
        success = False
        return redirect(url_for('register'))
      elif password1 != password2: 
        message = "Passwords do not match. Please try again."
        print(message)
        success = False
        return redirect(url_for('register')) 
    
  if success == True:
    mongo.db.user.insert_one({"name":name, "username":username, "email":email, "p":password1})
    session["username"] = username
    return redirect(url_for('newlisting', user=username))

@app.route('/newlisting/<user>', methods=['GET', 'POST'])
def newlisting(user):
  if request.method == 'GET':
    return render_template('newlisting.html', user=user)
  else:
    photo = request.form.get('photo')
    name = request.form.get('name')
    print(name)
    category = request.form.get('category')
    condition = request.form.get('condition')
    bookformat = request.form.get('type')
    classes = request.form.get('classes')
    price = request.form.get('price')
    timedate = datetime.now()
    user = user
    mongo.db.listing.insert_one({"photo":photo, "name":name, "category":category, "condition":condition, "bookformat":bookformat, "classes":classes, "price":price, "timedate":timedate, "user":user})
    return redirect(url_for('viewListing', user=user))

@app.route('/viewListing/<user>', methods=['GET', 'POST'])
def viewListing(user):
  if request.method == 'GET':
    listingdb = mongo.db.listing.find({})
    return render_template("displaylisting.html", user=user, listingdb=listingdb)

@app.route('/chat/<user>/<user2>', methods=['GET', 'POST'])
def chat2(user, user2):
  if request.method == 'GET':
    messages = mongo.db.message.find({})
    return render_template('chat.html', user=user, user2=user2, messages=messages)
  else:
    message = request.form.get('message')
    user_from = user
    user_to = user2
    times = datetime.now()
    mongo.db.message.insert_one({"user_from":user_from, "user_to":user_to, "message":message, "time":times})
    return redirect(url_for('chat2', user=user_from, user2=user_to))
    
@app.route('/allChats/<user>', methods=['GET', 'POST'])
def viewChat(user):
  if request.method == 'GET':
    messages = mongo.db.message.find({})
    users = mongo.db.user.find({})
    return render_template('allchats.html', users=users, user=user, messages=messages)     

@app.route('/chatting/<user>/<user2>', methods=['GET', 'POST'])
def chatting(user, user2):
  if request.method == 'GET':
    messages = mongo.db.message.find({})
    return render_template('chatting.html', user=user, user2=user2, messages=messages)
  else:
    message = request.form.get('message')
    user_from = user
    user_to = user2
    times = datetime.now()
    mongo.db.message.insert_one({"user_from":user_from, "user_to":user_to, "message":message, "time":times})
    return redirect(url_for('chatting', user=user_from, user2=user_to))

@app.route('/drop/<name>', methods=['GET', 'POST'])
def drop(name):
  listing = mongo.db.listing.find({})
  for l in listing:
    if l['name'] == name:
      user = l['user']
      mongo.db.listing.remove({"name": name})
      return redirect(url_for('viewListing', user=user))

@app.route('/about/<user>', methods=['GET'])
def about(user):
  return render_template('about.html', user=user)

@app.route('/logout')
def logout():
  session.pop('username', None)
  print("User Logged out")
  return redirect(url_for('home'))

app.run(host='0.0.0.0', port=8080)