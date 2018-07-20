# Python 2 program, due to enki

from SimpleHTTPServer import *
from BaseHTTPServer import *
#import http.server
import time
import json
import enki
from absl.app import run

import copy

HOST_NAME = "localhost"
PORT_NUMBER = 8000
KEY_PATH = "key.txt"
user_details_fields = ["age", "gender", "location"]
# This class contains methods to handle our requests to different URIs in the app
class ComputationServer(SimpleHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
 
    # Check the URI of the request to serve the proper content.
    def do_GET(self):
        if "getcomputation" in self.path:
            # Save arguments from URL query string
            arg_data = self.retrieve_url_arguments(self.path)

            task_runs = download_task_runs()
            # Try to find back our user id in tasks, by searching for our personal data
            user_id = lookup_userid_from_details(arg_data, task_runs)
            retr_details = lookup_details_from_userid(user_id, task_runs)
            print(user_id)
            print(retr_details)
            content = {"age": 11, "gender":"m","location":"Leiden"}
            content_string = json.dumps(content)
            self.respond(content_string) # we can retrieve response within this scope and then pass info to self.respond
 
    def handle_http(self, data):
        self.send_response(200)
        # set the data type for the response header. In this case it will be json.
        # setting these headers is important for the browser to know what 	to do with
        # the response. Browsers can be very picky this way.
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        #return bytes(data, 'UTF-8') # python 3
        return str(data).encode('UTF-8')
 
     # store response for delivery back to client. This is good to do so
     # the user has a way of knowing what the server's response was.
    def respond(self, data):
        response = self.handle_http(data)
        self.wfile.write(response)
    
    '''
    Returns dictionary of all arguments in query string
    '''
    def retrieve_url_arguments(self, url):
        # Save arguments from URL query string
        arguments_string = url.split("?")[-1]
        arguments = arguments_string.split("&")
        data = {}
        for arg in arguments:
            key, value = arg.split("=")
            data[key] = value
        return data
    
def download_task_runs():
    with open(KEY_PATH, "r") as f:
        key = f.read()
    e = enki.Enki(api_key=key, endpoint='http://localhost:5000',project_short_name='opentaal',all=1)
    e.get_all()
    return e.task_runs_df

    

def lookup_userid_from_details(user_data, tasks):
    user_ids = []
    for t in tasks:
        task = tasks[t]
        # Per task df, every user run is a row
        for run in task.itertuples():
            run_info = run.info
            if isinstance(run_info, dict):
                # If user info of this current user is in task
                if (user_data.viewitems() <= run_info.viewitems()):
                    user_ids.append(run.user_id)
    if len(user_ids) < 1:
        raise ValueError("No user id found for user details.")
    # Return first user id
    return user_ids[0]

def lookup_details_from_userid(userid, tasks):
    return_details = None
    for t in tasks:
        task = tasks[t]
        for run in task.itertuples():
            if run.user_id == userid:
                # If user id matches, check if this run contains user details
                run_info = run.info
                if all(key in run_info for key in user_details_fields):
                    return_details = run_info
                    break
    if return_details is None:
        raise ValueError("No user details found for user id.")
    return return_details
# This is the main method that will fire off the server. 
if __name__ == '__main__':
    server_class = HTTPServer # use http.server for python3
    httpd = server_class((HOST_NAME, PORT_NUMBER), ComputationServer)
    print((time.asctime(), 'Server Starts - %s:%s' % (HOST_NAME, PORT_NUMBER)))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print((time.asctime(), 'Server Stops - %s:%s' % (HOST_NAME, PORT_NUMBER)))
