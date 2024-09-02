from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
import event as evt
import user as usr

import os

# Flask App Initialization
app = Flask(__name__)
app.secret_key = 'my_random_key'  # Needed to use sessions

SERVER_HOST = os.environ.get('SERVER_HOST', 'localhost')
SERVER_PORT = int(os.environ.get('SERVER_PORT', 5000))
MONGO_DATABASE = os.environ.get('MONGO_DATABASE', 'eventsdb')
MOGNO_HOST = os.environ.get('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.environ.get('MONGO_PORT', 27017))

# MongoDB Client Initialization
client = MongoClient(MOGNO_HOST, MONGO_PORT)
db = client[MONGO_DATABASE]  # Database name
events_collection = db["events"]
users_collection = db["users"]

""" Routes """
# Home Route to Home Template
@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        type = session['type']
        email = session['email']
        fullname = session['fullname']
        return render_template('home.html', username=username, type=type)
    else:
        return render_template('home.html', username="", type="visitor")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        result = usr.user.login(username, password)
        if result[0] == None:
            error = "Unknown User"
        elif result[4] == None: 
            error = "Invalid Credentials"
        else:
            session['username'] = result[0]
            session['type'] = result[4]
            session['fullname'] = result[1]+" "+result[2]
            session['email'] = result[3]
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    # Remove the username from the session if it's there
    session.pop('username', None)
    session.pop('type', None)
    session.pop('fullname', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    try:
        if session['type']!="admin":
            return render_template('home.html')
    except:
        pass
    if request.method != 'POST':
        return render_template('add_user.html')
    else:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']
        type = "user"
        if firstname and lastname and email and password and password == confirm:
            ok = True
            if usr.user.get_from_db(username) != None:
                ok = False
                flash('Selected username already exists!', 'danger')
            if usr.user.get_from_db_by_email(email) != None:
                ok = False
                flash('Email already exists!', 'danger')
            if ok:
                User = usr.user(None, firstname, lastname, email, type, username, password)
                User.save_to_db()
                flash('User added successfully!', 'success')
        else:
            flash('Error in password conformation!', 'danger')
        return render_template('add_user.html')

@app.route('/participateevent/<id>/<status>/<who>', methods=['GET'])
def participate_in_event(id, status, who):
    if 'username' not in session:
        return redirect(url_for('login'))
    Event = evt.event.get_from_db(id)
    for e in Event.participants:
        if e['user'] == who:
            e['status'] = status
            evt.event.update_in_db(id, {"participants":Event.participants})
            user = who
            myEvents = evt.event.get_user_parts_event_from_db(who)
            return render_template('my_events.html', data=myEvents)
    Event.participants.append({"user":who, "status": status})
    evt.event.update_in_db(id, {"participants":Event.participants})
    user = who
    myEvents = evt.event.get_user_parts_event_from_db(who)
    return render_template('my_events.html', data=myEvents)
    
@app.route('/add_event', methods=['POST','GET'])
def add_event():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        type = request.form['type']
        date = request.form['date']
        time = request.form['time']
        
        from datetime import datetime
        past = datetime.strptime(date, "%Y-%m-%d")
        present = datetime.now()
        if past.date() < present.date():
            flash('Check the date given', 'danger')
        elif title and location and description and type and date and time:
        
            Event = evt.event(0,title,description,date,time,location,type,session['username'])
            Event.save_to_db()
            flash('Event added successfully!', 'success')
        else:
            flash('Error in data given', 'danger')
    return render_template('add_event.html')

@app.route('/myevents', methods=['GET'])
def my_events():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = session['username']
    myEvents = evt.event.get_user_event_from_db(user)
    return render_template('my_events.html', data=myEvents)

@app.route('/searchevents', methods=['GET', 'POST'])
def search_events():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = session['username']
    if request.method == 'POST':
        Events = evt.event.get_db_collection()
        title = request.form['title']
        location = request.form['location']
        type = request.form['type']
        lst = []
        from datetime import datetime
        
        present = datetime.now()
        
        for e in Events.find():
            ok = True
            past = datetime.strptime(e['day'], "%Y-%m-%d")
            if not ((title!="" and title in e['title']) or title == ""):
                ok = False
            if not ((location!="" and location in e['place']) or location == ""): 
                ok = False
            if not ((type!="all" and type  == e['type']) or type == "all"): 
                ok = False
            if past.date() < present.date():
                ok = False
            if ok:
                lst.append(e)
        return render_template('search_event.html', data=lst)
    else:
        return render_template('search_event.html', data=[])


@app.route('/searchusers', methods=['GET', 'POST'])
def search_users():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = session['username']
    type = session['type']
    if request.method == 'POST' and type=="admin":
        Users = usr.user.get_db_collection()
        username = request.form['username']
        email = request.form['email']
        name = request.form['name']
        lst = []
        for e in Users.find():
            ok = True
            if not ((email!="" and email in e['email']) or email == ""):
                ok = False
            if not ((username!="" and usrname in e['username']) or username == ""): 
                ok = False
            if not ((name!="" and (name  in e['firstname'] or name in e['lastname'])) or name == ""): 
                ok = False
            if ok:
                lst.append(e)
        return render_template('search_user.html', data=lst)
    else:
        return render_template('search_user.html', data=[])



@app.route('/mypartevents', methods=['GET'])
def my_part_events():
    if 'username' not in session:
        return redirect(url_for('login'))            
    user = session['username']
    myEvents = evt.event.get_user_parts_event_from_db(user)
    return render_template('my_events.html', data=myEvents)

@app.route('/event/<id>', methods=['GET'])
def this_event(id):
    if 'username' not in session:
        return redirect(url_for('login'))            
    user = session['username']
    mydata = evt.event.get_from_db(id)
    return render_template('this_event.html', data=mydata)


@app.route('/user/<id>', methods=['GET'])
def this_user(id):
    if 'username' not in session:
        return redirect(url_for('login'))            
    user = session['username']
    mydata = usr.user.get_from_db(id)
    return render_template('this_user.html', data=mydata)


@app.route('/event/delete/<id>', methods=['GET'])
def delete_this_event(id):
    if 'username' not in session:
        return redirect(url_for('login'))            
    user = session['username']
    Event = evt.event.get_from_db(id)
    result = "Event removed from schedule"
    if Event.owner == session['username'] or session['type'] == "admin":
        evt.event.delete_from_db(id)
    else: 
        result = "Event could not be removed from schedule"
    return render_template('this_event_deleted.html', result=result)

@app.route('/user/delete/<id>', methods=['GET'])
def delete_this_user(id):
    if 'username' not in session:
        return redirect(url_for('login'))   
    if session['type']!="admin":
        return redirect(url_for('home'))
    User = usr.user.get_from_db(id)
    result = "User removed from system"
    usr.user.delete_from_db(id)
    return render_template('this_user_deleted.html', result=result)


from datetime import datetime

def datetimeformat(value, format='%Y-%m-%d'):
    return datetime.strptime(value, '%d/%m/%Y').strftime(format)


@app.route('/event/update/<id>', methods=['GET','POST'])
def update_this_event(id):
    if 'username' not in session:
        return redirect(url_for('login'))            
    user = session['username']
    if request.method == "GET":
        d = evt.event.get_from_db(id)
        return render_template('this_event_update.html', data = d)
    elif request.method == "POST":
        title = request.form['title']
        location = request.form['location']
        date = request.form['date']
        time = request.form['time']
        description = request.form['description']
        type = request.form['type']
        
        if title and location and description and type and date and time:
            d = {"title":title, "place":location, "day":date, "time":time, "description": description, "type":type}
            evt.event.update_in_db(id, d)
            flash('Event updated successfully!', 'success')
        else:
            flash('Error!!!', 'danger')
        dnew = evt.event.get_from_db(id)
        return render_template('this_event_update.html', data=dnew)
    
@app.route('/user/update/<id>', methods=['GET','POST'])
def update_this_user(id):
    if 'username' not in session:
        return redirect(url_for('login'))            
    user = session['username']
    if request.method == "GET" and (session['type']=="admin" or user == id):
        d = usr.user.get_from_db(id)
        return render_template('this_user_update.html', data = d)
    elif request.method == "POST":
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']
        type = "user"
        d = {}
        if firstname and lastname and email and password and password == confirm:
            ok = True
            res = usr.user.get_from_db(username)
            print(res," ",id,(res != None and res.username!=id))
            if res != None and res.username!=id:
                ok = False
                flash('Selected username already exists!', 'danger')
            res1 = usr.user.get_from_db_by_email(email)
            if res1 != None and res1.email!=res.email:
                ok = False
                flash('Email already exists!', 'danger')
            if ok:
                d = {"firstname":firstname, "lastname":lastname, "email":email, "username":username, "password":password}
                usr.user.update_in_db(id, d)
                flash('User updated successfully!', 'success')
        else:
            flash('Error in password conformation!', 'danger')
        return render_template('this_user_update.html', data=d)
    


# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True, host=SERVER_HOST, port=SERVER_PORT)