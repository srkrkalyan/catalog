from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Hello!</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>&#161 Hola !</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants"):
            	self.send_response(200)
            	self.send_header('Content-type', 'text/html')
                self.end_headers()
            	output = ""
            	name=""
            	restaurants = session.query(Restaurant).all()
            	for each in restaurants:
            		output = output + "<html><head><h1>%s</h1></head></html>"%(each.name,)+\
            					"<a href='#'>Edit</a><br><a href='#'>Delete</a>"

            	self.wfile.write(output)
            	return

            if self.path.endswith("/restaurants/new"):
            	self.send_response(200)
            	self.send_header('Content-type', 'text/html')
            	self.end_headers()
            	output = """<html><head>
            				<form method='post'>
            				<h1>Add a new restaurant</h1>
            				<input type="text" name="restaurant_name">
            				<input type='Submit' name='Submit'>
            				</form>
            				</head>
            				</html>
            			"""
            	self.wfile.write(output)
            	print output
            	return

            if self.path.endswith("/delete"):
            	self.send_response(200)
            	restaurants = session.query(Restaurant).all()
            	#session.commit()
            	print len(restaurants)

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


    def do_POST(self):
        try:
        	if self.path.endswith("/restaurants/new"):
        		self.send_response(301)
        		self.send_header('Content-type', 'text/html')
        		self.end_headers()
        		ctype, pdict = cgi.parse_header(
        			self.headers.getheader('content-type'))
        		if ctype == 'multipart/form-data':
        			fields = cgi.parse_multipart(self.rfile, pdict)
	                messagecontent = fields.get('restaurant_name')
        		print messagecontent

        	else:
	            self.send_response(301)
	            self.send_header('Content-type', 'text/html')
	            self.end_headers()
	            ctype, pdict = cgi.parse_header(
	                self.headers.getheader('content-type'))
	            if ctype == 'multipart/form-data':
	                fields = cgi.parse_multipart(self.rfile, pdict)
	                messagecontent = fields.get('message')
	            output = ""
	            output += "<html><body>"
	            output += " <h2> Okay, how about this: </h2>"
	            output += "<h1> %s </h1>" % messagecontent[0]
	            output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
	            output += "</body></html>"
	            self.wfile.write(output)
	            print output
        except:
            pass


def main():
    try:
        port = 8001
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()