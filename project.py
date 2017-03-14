from flask import Flask, render_template
from flask import request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


app = Flask(__name__)


@app.route('/login')
def login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state']  = state
	return render_template("login.html", STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
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
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    #data = answer.json()
    data = json.loads(answer.text)

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    #see if user exists, if not add user to db

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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
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


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    #print stored_credentials
    if 'username' not in login_session:
		return redirect('/login')
    #print login_session.keys()
    access_token = login_session['access_token']
    if access_token is None:
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['username']
    if access_token is None:
 		print 'Access Token is None'
 		response = make_response(json.dumps('Current user not connected.'), 401)
 		response.headers['Content-Type'] = 'application/json'
 		return response
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
		response = make_response(json.dumps('Successfully Disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
    else:
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

@app.route('/')
@app.route('/restaurant')
def homePage():
	restaurants = session.query(Restaurant).all()
	return render_template("homepage.html",restaurants=restaurants)


@app.route('/restaurant/json')
def restaurantJSON():
	restaurants = session.query(Restaurant).all()
	return jsonify(Restaurants=[i.serialize for i in restaurants])


@app.route('/restaurant/new',methods = ['POST', 'GET'])
def newRestaurant():
	if 'username' not in login_session:
		return redirect('/login')
	if request.method == 'POST':
		newRestaurant = Restaurant(name = request.form['new_restaurant_name'])
		session.add(newRestaurant)
		session.commit()
		return redirect(url_for('homePage'))
	else:
		return render_template("newrestaurant.html")


@app.route('/restaurant/<int:restaurant_id>/edit',methods = ['POST', 'GET'])
def editRestaurant(restaurant_id):
	if 'username' not in login_session:
		return redirect('/login')
	if request.method == 'POST':
		restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
		restaurant.name = request.form['edited_value']
		session.add(restaurant)
		session.commit()
		return redirect(url_for('homePage'))
	else:
		restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
		return render_template("editrestaurant.html",restaurant = restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete',methods = ['POST', 'GET'])
def deleteRestaurant(restaurant_id):
	if 'username' not in login_session:
		return redirect('/login')
	if request.method == 'POST':
		restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
		session.delete(restaurant)
		session.commit()
		return redirect(url_for('homePage'))
	else:
		restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
		return render_template("deleterestaurant.html",restaurant = restaurant)


@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	menu = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
	return jsonify(Menu_Items=[i.serialize for i in menu])

@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
	if 'username' not in login_session:
		return redirect('/login')
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	menu = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
	return render_template("menu.html", restaurant = restaurant, items=menu)

@app.route('/restaurants/new/<int:restaurant_id>/', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
	if 'username' not in login_session:
		return redirect('/login')
	if request.method == 'POST':
		newItem = MenuItem(name = request.form['item_name'], restaurant_id = restaurant_id,
			description = request.form['item_description'],
			price = request.form['item_price'],
			course = request.form['item_category'])
		session.add(newItem)
		session.commit()
		flash("New menu item created")
		return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
	else:
		return render_template("newmenuitem.html",restaurant_id = restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/JSON') 
def editMenuItemJSON(restaurant_id,menu_id):
	menuName = session.query(MenuItem).filter_by(id = menu_id).one()
	return jsonify(menuName.serialize)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods = ['POST', 'GET'])
def editMenuItem(restaurant_id,menu_id):
	if 'username' not in login_session:
		return redirect('/login')
	if request.method == 'POST':
		menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
		menuItem.name = request.form['edited_value']
		session.add(menuItem)
		session.commit()
		flash("Menu item successfully edited")
		return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
	else:
		menuName = session.query(MenuItem).filter_by(id = menu_id).one().name
		return render_template("editmenuitem.html",restaurant_id = restaurant_id, itemname = menuName, menu_id = menu_id)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods = ['POST', 'GET'])
def deleteMenuItem(restaurant_id,menu_id):
	if 'username' not in login_session:
		return redirect('/login')
	if request.method == 'POST':
		menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
		session.delete(menuItem)
		session.commit()
		flash("Menu Item Deleted")
		return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
	else:
		menuName = session.query(MenuItem).filter_by(id = menu_id).one().name
		return render_template("deletemenuitem.html",restaurant_id = restaurant_id, itemname = menuName, menu_id = menu_id)


if __name__ == '__main__':
	app.secret_key = 'secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
