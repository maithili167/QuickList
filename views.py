"""
Routes and views for the flask application.
"""

import datetime
from flask import Flask,render_template,request,session,redirect,url_for
from FlaskAzure import app
from pymongo import MongoClient
import base64
import os
from bson.objectid import ObjectId

SIZE=50000
LIMIT=5
HOST='*********'
app.secret_key='*******'

@app.route('/')
def login():
     return render_template("login.html")

@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page'
        #year=datetime.now().year,
    )


# register for the application
@app.route("/signup",methods=['GET','POST'])
def signup():
    username=request.form['myusername']
    password = request.form['mypassword']
    client = MongoClient(HOST)
    users = client.mydb.users
    existing=users.find_one({"username": username})
    if existing is None:
        users.insert({"username": username,"password":password})
        session['username']=username
        return redirect(url_for('home'))
    return "Username already exists"


#login into the application
@app.route('/login',methods=['GET','POST'])
def welcome():
    username=request.form['username']
    password=request.form['password']
    client = MongoClient(HOST)
    users = client.mydb.users
    login_user = users.find_one({"username": username})
    if login_user:
        if login_user['password']==password:
            session['username']=username
            return redirect(url_for('home'))
        return "Invalid username/password"
    return "Invalid username"


#create a todo list
@app.route('/upload',methods=['GET','POST'])
def upload():
    file_to_upload = request.files['mypic']
    subject = request.form['subject']
    priority = request.form['priority']
    client = MongoClient(HOST)
    todo = client.mydb.todo
    name, ext = os.path.splitext(file_to_upload.filename)

    ##check file size and restrict upload if greater than specified value
    #fsize=os.stat(file_to_upload.filename).st_size
    #if fsize>=SIZE:
    #    return "limit exceeded"
    #cursor = todo.find({"username":session['username']})
    ##check number of list items and restrict upload if greater than specified value
    #if cursor.count()>=LIMIT:
    #    return "limit exceeded"
    if ext  in ('.txt'):
        readfile = file_to_upload.read()
        encoded_string = readfile
        type="text"
    else:
        readfile = file_to_upload.read()
        encoded_string = base64.b64encode(readfile)
        type="image"
    #save list item in database
    #todo.insert({"image": encoded_string,"username":session['username'],"subject":subject,"priority":priority,"uploadtime":datetime.datetime.now()})
    todo.insert({"filecont": encoded_string,"filetype":type,"username":session['username'],"subject":subject,"priority":priority,"uploadtime":datetime.datetime.now()})
    #fetch list items from database
    cursor = todo.find({"username":session['username']})
    images=[]
    for data in cursor:
        images.append(data)
    client.close()
    return render_template("pictures.html", images=images)

# show my todo list
@app.route("/showlist",methods=['GET','POST'])
def showlist():
    category=request.form['category']
    client = MongoClient(HOST)
    todo = client.mydb.todo
    #fetch list items from database based on sort category
    cursor = todo.find({"username":session['username']}).sort([(category, -1)])
    images=[]
    print "category:"+category
    for data in cursor:
        images.append(data)
    client.close()
    return render_template("pictures.html", images=images)


# remove list items
@app.route("/remove",methods=['GET','POST'])
def remove():
    _id=request.args.get('_id')
    client = MongoClient(HOST)
    todo = client.mydb.todo
    #delete selected list item
    todo.delete_one({"_id": ObjectId(_id)})
    cursor = todo.find({"username":session['username']})
    images=[]
    for data in cursor:
        images.append(data)
    client.close()
    return render_template("pictures.html", images=images)

@app.route("/search",methods=['GET','POST'])
def search():
    item=request.form['item']
    client = MongoClient(HOST)
    todo = client.mydb.todo
    #search selected list item
    cursor = todo.find({"$text":{"$search":item}})
    images=[]
    for data in cursor:
        images.append(data)
    client.close()
    return render_template("pictures.html", images=images)

@app.route("/sort",methods=['GET','POST'])
def sort():
    mins=request.form['mins']
    mins=int(mins)
    client = MongoClient(HOST)
    todo = client.mydb.todo
    uploadtime=datetime.datetime.now() - datetime.timedelta(minutes=mins)
    #search selected list item
    cursor = todo.find({"uploadtime": {"$lt": uploadtime}})
    images=[]
    for data in cursor:
       
        images.append(data)
    client.close()
    return render_template("pictures.html", images=images)     


@app.route("/logout")
def logout():
    session["__invalidate__"] = True
    return redirect(url_for("login"))

@app.route('/contact')
def contact(): 
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
