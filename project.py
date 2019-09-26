
from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CatItem, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog" 

# Init DATABASE
engine = create_engine('sqlite:///sportitmes.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Funtions for user log in-----------------------------------------
@app.route('/login')
def showLogin():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
        access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abandon ship.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify the access token is valid for the catalog app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    # See if the user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user information
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if user exists, if it doesn't, make a new user record
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px; \
    -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print ("done!")
    return output

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Json for CATALOG--------------------------------------------------
@app.route('/Catalog/JSON')
def catalogJSON():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Items = session.query(CatItem).all()
    return jsonify(CatItem=[i.serialize for i in Items])


# CRUD FUNCTIONS ---------------------------------------------------
@app.route('/')
@app.route('/catalog')
def showCategories():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Categories = session.query(Category).all()
    Items = session.query(CatItem).all()
    return render_template('home.html', Categories = Categories, Items = Items)

@app.route('/catalog/<cat_name>')
@app.route('/catalog/<cat_name>/items')
def showItems(cat_name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Categories = session.query(Category).all()
    Cat = session.query(Category).filter_by(name = cat_name).one()
    Items = session.query(CatItem).filter_by(cat_name = Cat.name)
    return render_template('items.html', Categories = Categories, Items = Items, Cat = Cat)


@app.route('/catalog/<cat_name>/<item_name>')
@app.route('/catalog/<cat_name>/<item_name>/<item_id>')
def ItemDescription(cat_name, item_name, item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Cat = session.query(Category).filter_by(name = cat_name).one()
    Item = session.query(CatItem).filter_by(id = item_id).one()
    return render_template('description.html', Cat = Cat, Item = Item, cat_name = cat_name)


@app.route('/catalog/<cat_name>/new', methods=['GET', 'POST'])
def createItem(cat_name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if request.method == 'POST':
        Items = session.query(Category).filter_by(name = cat_name)
        newItem = CatItem(
        name = request.form['name'],
        description = request.form['Description'],
        cat_name = cat_name)
        session.add(newItem)
        session.commit()
        return redirect(url_for('showItems', cat_name = cat_name))
    else:
        return render_template('createItem.html', cat_name = cat_name)


@app.route('/catalog/<cat_name>/<item_name>/<item_id>/edit', methods=['GET', 'POST'])
def editItems(cat_name, item_name, item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    editedItem = session.query(CatItem).filter_by(id = item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['Description']:
            editedItem.description = request.form['Description']
        if request.form['Category']:
            editedItem.cat_name = request.form['Category']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showItems', cat_name = cat_name))
    else:
        return render_template(
            'editItem.html', cat_name=cat_name, item_name = item_name, item_id = item_id )

@app.route('/catalog/<cat_name>/<item_name>/<item_id>/delete', methods=['GET', 'POST'])
def deleteItem(cat_name, item_name, item_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    itemToDelete = session.query(CatItem).filter_by(id = item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showItems', cat_name = cat_name))
    else:
        return render_template('deleteItem.html', cat_name = cat_name, itemToDelete = itemToDelete)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
