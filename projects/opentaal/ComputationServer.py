import http.server
import time
import json

HOST_NAME = "localhost"
PORT_NUMBER = 8080
# This class contains methods to handle our requests to different URIs in the app
class ComputationServer(http.server.SimpleHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
 
    # Check the URI of the request to serve the proper content.
    def do_GET(self):
        if "getcomputation" in self.path:
        	# If URI contains URLToTriggerGetRequestHandler, execute the python script that corresponds to it and get that data
            # whatever we send to "respond" as an argument will be sent back to client
            content = {"age": 24}
            content_string = json.dumps(content)
            self.respond(content_string) # we can retrieve response within this scope and then pass info to self.respond
        #else:
        #    super(ComputationServer, self).do_GET() #serves the static src file by default
 
    def handle_http(self, data):
        self.send_response(200)
        # set the data type for the response header. In this case it will be json.
        # setting these headers is important for the browser to know what 	to do with
        # the response. Browsers can be very picky this way.
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        return bytes(data, 'UTF-8')
 
     # store response for delivery back to client. This is good to do so
     # the user has a way of knowing what the server's response was.
    def respond(self, data):
        response = self.handle_http(data)
        self.wfile.write(response)
 
# This is the main method that will fire off the server. 
if __name__ == '__main__':
    server_class = http.server.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), ComputationServer)
    print((time.asctime(), 'Server Starts - %s:%s' % (HOST_NAME, PORT_NUMBER)))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print((time.asctime(), 'Server Stops - %s:%s' % (HOST_NAME, PORT_NUMBER)))