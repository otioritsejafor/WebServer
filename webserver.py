from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

#CRUD operations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


#Connect to database
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:

			if self.path.endswith("/hello"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>Hello!"
				output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2> What would you like me to say? </h2><input name = 'message' type='text'><input type='submit' value='Submit'></form>"
				output += "<body></html>"
				self.wfile.write(output)
				print output
				return

			if self.path.endswith("/hola"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>&#161Hola! <a href = '/hello'> Back to Hello </a>"
				output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2> What would you like me to say? </h2><input name = 'message' type='text'><input type='submit' value='Submit'></form>"
				output += "<body></html>"
				self.wfile.write(output)
				print output
				return

			if self.path.endswith("/restaurants"):
				restaurants = session.query(Restaurant).all()
				output = ""
				output += "<a href='/restaurants/new'><h2> Make a New Restaurant Here </h2></a></br></br>"

				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output += "<html><body>"
				for place in restaurants:
					output += "<h3>{code}</h3></br>".format(code = place.name)
					output += "<a href ='/restaurants/{Id}/edit' >Edit </a></br>".format(Id = place.id)
					output += "<a href =' /restaurants/{Id}/delete'> Delete </a>".format(Id = place.id)
					output += "</br></br></br>"

				output += "</body></html>"
				self.wfile.write(output)
				return

			if self.path.endswith("/restaurants/new"):
			 	self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body>"
				output += "<h1>Create a New Restaurant</h1>"
				output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/new'><input name = 'new_restaurant' type = 'text' placeholder = 'Enter Restaurant Name' ><input type='submit' value='Create'>"
				output += "</form></body></html>"
				self.wfile.write(output)
				return

			if self.path.endswith("/edit"):
				IdPath = self.path.split("/")[2]
				restaurantQuery = session.query(Restaurant).filter_by(id=IdPath).one()
				if restaurantQuery != []:
			 		self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = ""
					output += "<html><body>"
					output += "<h1>{name}</h1>".format(name = restaurantQuery.name)
					output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/" + str(IdPath) + "/edit'>"
					output += "<input name = 'new_name' type = 'text' placeholder = '{restaurant_name}' ><input type='submit' value='Rename'>".format(restaurant_name=restaurantQuery.name)
					output += "</form></body></html>"
					self.wfile.write(output)
					return

			if self.path.endswith("/delete"):
				IdPath = self.path.split("/")[2]
				unwantedRestaurant = session.query(Restaurant).filter_by(id=IdPath).one()
				if unwantedRestaurant != []:
			 		self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = ""
					output += "<html><body>"
					output += "<h1>Are you sure you want to delete {name}?</h1>".format(name = unwantedRestaurant.name)
					output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/" + str(IdPath) + "/delete'>"
					output += "<input type='submit' value='Delete'>"
					output += "</form></body></html>"
					self.wfile.write(output)
					return

		except IOError:
			self.send_error(404, "File not found %s" % self.path)

	def do_POST(self):
		try:
			if self.path.endswith("/restaurants/new"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
				restaurantAdded = fields.get('new_restaurant')

				newRestaurant = Restaurant(name = restaurantAdded[0])
				session.add(newRestaurant)
				session.commit()

			
			if self.path.endswith("/edit"):
				IdPath = self.path.split("/")[2]
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
				newName = fields.get('new_name')

				restaurantQuery = session.query(Restaurant).filter_by(id=IdPath).one()
				if restaurantQuery != []:					
					restaurantQuery.name = newName[0]
					session.add(restaurantQuery)
					session.commit()
			
			if self.path.endswith("/delete"):
				IdPath = self.path.split("/")[2]
				#ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				#if ctype == 'multipart/form-data':
				#	fields = cgi.parse_multipart(self.rfile, pdict)

				unwantedRestaurant = session.query(Restaurant).filter_by(id=IdPath).one()
				if unwantedRestaurant != []:					
					session.delete(unwantedRestaurant)
					session.commit()	

			self.send_response(301)
			self.send_header('Content-type', 'text/html')
			self.send_header('Location', '/restaurants')
			self.end_headers()

		except:
			pass


			


def main():
	try:
		port = 8080
		server = HTTPServer(('', port), webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()

	except KeyboardInterrupt:
		print "^C entered, stopping web server..."
		server.socket.close()



if __name__ == '__main__':
	main()
