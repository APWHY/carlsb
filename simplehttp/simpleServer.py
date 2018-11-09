# This entire package is mainly for demo purposes. 


import http.server
import socketserver
import os
import shutil
from common import utils,consts




# This class sets up a simple HTTP server that is set up to serve the 'example' file in the 'download' folder
# The file will be returned on any get request.
class SimpleFileHandler(http.server.BaseHTTPRequestHandler):
    serving = os.path.join(os.path.curdir, 'simplehttp', 'download','example') # default, can be overridden
    def do_GET(self):
        f = open(self.serving,'rb') 
        self.send_response(200)
        self.send_header("Content-type", 'text/plain')
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        shutil.copyfileobj(f,self.wfile)
        f.close()
        
# simple test code        
if __name__ == "__main__": # must run this from root dir or it won't work

    handler = SimpleFileHandler
    ip = utils.get_ip()

    with socketserver.TCPServer((ip,consts.HTTP_PORT), handler) as httpd:
        print("serving at port", consts.HTTP_PORT)
        print("serving at address", ip)
        httpd.serve_forever()
