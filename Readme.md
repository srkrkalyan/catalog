This repo contains complete code base for a web application 'Restaurant Menu App'. This app was designed and developed as part of Udacity Full Stack Web Development Nanodegree program.

Features of this application:

1. Uses Google oAuth for user authentication
2. Logged in user can create/edit/delete a new/existing restaurant
3. Logged in user can create/edit/delete a new/existing menu item if she owns the restaurant
4. User can still able to view list of restaurants and its menu items without logging into the application

Technology:

This application was developed in Python using web development framework "Flask". This app uses SQLite as backened data base. Data layer is integrated with business logic (actual application server code) using SQL alchemy, an ORM (Object Relational Model) framework. Also, for intuitive user interface, this app is using Twitter Bootstrap CSS templates (ofcourse, very minimal)


Running this application in local machine:

This application has not deployed on any public cloud yet. So, to run this application, clone the entire github repository and run "project.py" file from command prompt. Based on above technical specifications, local machine (environment) should have below python modules as pre-requisite to running this app.

1. Flask
2. Sqlalchemy
3. oAuth2client
4. httplib2
5. json

Web Services Layer:

This application exposes below REST services for other apps to consume the restaurant/menu information.

1. ../restaurant/json - Provides complete list of available restaurants in JSON format
2. ../restaurants/<int:restaurant_id>/menu/JSON - Provides complete menu details for requested restaurant in JSON format

