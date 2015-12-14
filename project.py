# primary imports for crud and flask

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup_list import Base, Subjects, Response, User
from functools import wraps
from flaskext.xmlrpc import XMLRPCHandler, Fault

# imports for login function

from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# define app name

app = Flask(__name__)

handler = XMLRPCHandler('api')
handler.connect(app, '/api')

# connect to project database

engine = create_engine('sqlite:///subjecsandrespnse.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# define methods to create users in database and get user information

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

def checkUser(email):
    user_id = getUserID(email)
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

# End create users

# Begins login functions and routes

@app.route('/login')
def showLogin():
    
    # create random state variable to protect against hacking
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    
    # display state code:
    # return "The current session state is %s" % login_session['state']

    # display login template:
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # check state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps("Invalid state parameter."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
    # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('secrets/g_client_secrets.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps("Failed to upgrade the authorization \
                                            code."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

# Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

# Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match \
                                            given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

# Verify that the access token is valid for this app.
    CLIENT_ID = json.loads(open('secrets/g_client_secrets.json',
                                'r').read())['web']['client_id']
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match \
                                            app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

# Verify if user is already logged in.
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("Current user is already connected."),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
            
# Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

# Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    
    data = answer.json()
    
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

#check for account and create new or set userid
    checkUser(login_session['email'])
    
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# deactivated route because I don't want people directly trying to logout via url
# @app.route('/gdisconnect')
def gdisconnect():
    
    # check if session is active
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('No user is connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # return fail or succeed dc to disconnect method
    if result['status'] == '200':
        response = make_response(json.dumps('Disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return "200"
    else:
        response = make_response(json.dumps('Failed to revoke. %s') % access_token,
                                 400)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # check state
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    #print "access token received %s " % access_token
    # check secrets
    app_id = json.loads(open('secrets/fb_client_secrets.json', 'r').\
                        read())['web']['app_id']
    app_secret = json.loads(open('secrets/fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
                            
    # use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]
                            
    # The token must be stored in the login_session in order to properly logout,
    # let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token
                            
    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
                            
    login_session['picture'] = data["data"]["url"]
                            
    #check for account and create new or set userid
    checkUser(login_session['email'])

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += login_session['facebook_id']
    
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    
    flash("Now logged in as %s" % login_session['username'])
    return output


# deactivated route because I don't want people directly trying to logout via url
# @app.route('/fbdisconnect')
def fbdisconnect():
    # check if already logged in
    if 'username' not in login_session:
        response = make_response(json.dumps('No user is connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    
    # return success or fail dc
    if result['status'] == "200":
        response = make_response(json.dumps('Disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        
        return "200"
    else:
        response = make_response(json.dumps('Failed to revoke. %s') % result, 400)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            test = gdisconnect()
            if test == "200":
                del login_session['gplus_id']
                del login_session['credentials']
            else:
                return test
        if login_session['provider'] == 'facebook':
            test = fbdisconnect()
            if test == "200":
                del login_session['facebook_id']
            else:
                return test
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('landing'))
    else:
        flash("You were not logged in")
        return redirect(url_for('landing'))

# End log in section

# Begin website routes

# restuarant information
# welcome page /
# all subjects /subjects                        - subjects.html
# view one subject /subjects/<>                 - respond.html
# create new subjects /subjects/new             - newsubjects.html
# edit subjects /subjects/<>/edit               - editsubject.html
# delete subjects /subjects/<>/delete           - none
# create new subject item /subjects/<>/new      - none
# delete subjects item /subjects/<>/<>/delete   - none
# censor posts /<>/<>/censor                    - none


def login_required(log):
    @wraps(log)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showLogin'))
        return log(*args, **kwargs)
    return decorated_function

# main landing page

@app.route('/')
@app.route('/index')
def landing():
    side = session.query(Subjects).order_by(desc(Subjects.id)).all()
    logged = login_session
    return render_template('index.html', logged = logged, side = side)

# display all subjects checks if user is logged in for posts

@handler.register
@app.route('/subjects/')
def showSubjects():
    side = session.query(Subjects).order_by(desc(Subjects.id)).all()
    # joins tables and gathers needed values from both
    subjects = session.query(Subjects).\
                        order_by(desc(Subjects.id)).\
                        join(Subjects.user).\
                        values(User.name,
                               User.picture,
                               Subjects.title,
                               Subjects.body,
                               Subjects.creation_date,
                               Subjects.id)
    return render_template('subjects.html',
                               subjects = subjects,
                               side = side)

# jsonify subjects

@app.route('/subjects/JSON')
def subjectsJSON():
    subjects = session.query(Subjects).all()
    return jsonify(subjects=[s.serialize for s in subjects])


# displays one subject and related posts checks for login

@handler.register
@app.route('/subjects/<int:subjects_id>', methods=['GET','POST'])
def ShowResponds(subjects_id):
    side = session.query(Subjects).order_by(desc(Subjects.id)).all()
    subjects = session.query(Subjects).filter_by(id = subjects_id).one()
    # joins tables and gathers needed values from both as well as sorting
    response = session.query(Response).\
                        filter_by(subjects_id = subjects_id).\
                        order_by(desc(Response.id)).\
                        join(Response.user).\
                        values(User.picture,
                               User.name,
                               Response.text,
                               Response.creation_date,
                               Response.id,
                               Response.user_id)
    # checks for post request and validity of post
    if request.method == 'POST':
        if len(request.form['text']) < 1 :
            flash("Please inlcude both title and subject")
            return render_template('respond.html')
        newpost = Response(text = request.form['text'],
                           user_id = login_session['user_id'],
                           subjects_id = subjects_id)
        session.add(newpost)
        session.commit()
        flash("New post created!")
        return redirect(url_for('ShowResponds', subjects_id = subjects_id))
    else:
        return render_template('respond.html',
                               subjects_id = subjects_id,
                               response = response,
                               subjects = subjects,
                               side = side)

# jsonify responses

@app.route('/subjects/<int:subjects_id>/JSON')
def responseJSON(subjects_id):
    response = session.query(Response).filter_by(subjects_id = subjects_id).all()
    return jsonify(Response=[r.serialize for r in response])


# creates new post if logged in

@app.route('/subjects/new', methods=['GET','POST'])
@login_required
def addTosubjects():
    if request.method == 'POST':
        if len(request.form['name']) < 1 or len(request.form['text']) < 1 :
            flash("Please inlcude both title and subject")
            return render_template('newsubjects.html')
        newsubject = Subjects(title = request.form['name'],
                       body = request.form['text'],
                       user_id = login_session['user_id'])
        session.add(newsubject)
        session.commit()
        flash("New subject %s created!" % newsubject.title)
        return redirect(url_for('showSubjects'))
    else:
        return render_template('newsubjects.html')

# edits subject and checks user authority

@app.route('/subjects/<int:subjects_id>/edit', methods=['GET','POST'])
@login_required
def editSubject(subjects_id):
    editedSubject = session.query(Subjects).filter_by(id=subjects_id).one()
    if editedSubject.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this subject. Please create your own subject in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['title']:
            editedSubject.title = request.form['title']
        if request.form['body']:
            editedSubject.body = request.form['body']
        session.commit()
        flash('Subject Edited')
        return redirect(url_for('ShowResponds', subjects_id = subjects_id))
    else:
        return render_template('editsubjects.html', subject=editedSubject)

# deletes subjecs or responses based on passed values

@app.route('/<int:subjects_id>/<int:response_id>/delete', methods=['GET'])
@login_required
def delete(subjects_id, response_id):
    if response_id == 0:
        deletedSubject = session.query(Subjects).filter_by(id=subjects_id).one()
        if deletedSubject.user_id != login_session['user_id']:
            return "<script>function myFunction() {alert('You are not authorized to edit this subject. Please create your own subject in order to edit.');}</script><body onload='myFunction()''>"
        session.delete(deletedSubject)
        flash('%s deleted!' % deletedSubject.title)
        session.commit()
        return redirect(url_for('showSubjects'))
    else:
        deletedResponse = session.query(Response).filter_by(id=response_id).one()
        if deletedResponse.user_id != login_session['user_id']:
            return "<script>function myFunction() {alert('You are not authorized to edit this subject. Please create your own subject in order to edit.');}</script><body onload='myFunction()''>"
        session.delete(deletedResponse)
        flash('post deleted!')
        session.commit()
        return redirect(url_for('ShowResponds', subjects_id = subjects_id))

# censors posts that the primay subject organizer doesnt like

@app.route('/<int:subjects_id>/<int:response_id>/censor', methods=['GET'])
@login_required
def censor(subjects_id, response_id):
    if response_id != 0:
        editedResponse = session.query(Response).filter_by(id=response_id).one()
        if subjects_id != login_session['user_id']:
            return "<script>function myFunction() {alert('You are not authorized to edit this subject. Please create your own subject in order to edit.');}</script><body onload='myFunction()''>"
        editedResponse.text = "*** censored *** by: "+login_session['username']
        flash('censored')
        session.commit()
        return redirect(url_for('ShowResponds', subjects_id = subjects_id))
    else:
        return redirect(url_for('ShowResponds', subjects_id = subjects_id))

# flask running server

if __name__ == '__main__':
    app.secret_key = 'SDUsdG2264tI&SD78godo3rP(*dorh2o928#$g3GFGSFG73rwd3122e4tgr3faw4wyhgOKIY78di3d'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
