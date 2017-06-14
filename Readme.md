This repo contains complete code base for a web application 'Restaurant Menu App'/'Catalog'. This app is designed and developed as part of Udacity Full Stack Web Development Nanodegree program. This app is deployed on a Ubuntu server hosted by AWS Lightsail.

Application Deployment Details:

1. Public IP of Ubuntu server: 54.191.149.137
2. URL of the application: 54.191.149.137/
3. Application works on default http port 80
4. Summary of software installed on Ubuntu server:
	a. apache2 web server
	b. Postgresql db server
	c. Python 2.7
	d. Python Build Utilities
	e. Python Packages:
		1. Flask
		2. Sqlalchemy
		3. oAuth2client
		4. httplib2
		5. json
5. Summary of server configuration:
	a. Configured /etc/ssh/sshd_config to listen on port 2200 instead of default port 22
	b. Added new user 'grader' and provided ssh, sudo access
	c. Configured ssh to accept remote connections with only key authentication, password authentication is disabled
	d. Configured apache web server to redirect all root '/' calls to catalog application's home page
	e. Created new DB user 'grader' for postgresql DB and created new database for application data

Running this application in local machine:

This app can be accessed via internet @ http://54.191.149.137/

Features of this application:

1. Uses Google oAuth for user authentication
2. Logged in user can create/edit/delete a new/existing restaurant
3. Logged in user can create/edit/delete a new/existing menu item if she owns the restaurant
4. User can still able to view list of restaurants and its menu items without logging into the application
5. Deployed on Ubuntu server hosted on Amazon Web Services (Lightsail)

Technology:

This application was developed in Python using web development framework "Flask". This app uses SQLite as backened data base. Data layer is integrated with business logic (actual application server code) using SQL alchemy, an ORM (Object Relational Model) framework. Also, for intuitive user interface, this app is using Twitter Bootstrap CSS templates (ofcourse, very minimal)

Web Services Layer:

This application exposes below REST services for other apps to consume the restaurant/menu information.

1. ../restaurant/json - Provides complete list of available restaurants in JSON format
2. ../restaurants/<int:restaurant_id>/menu/JSON - Provides complete menu details for requested restaurant in JSON format

