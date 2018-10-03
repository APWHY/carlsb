import http.server
import socketserver
import os
import shutil
from common import utils,consts





class SimpleFileHandler(http.server.BaseHTTPRequestHandler):
    serving = os.path.join(os.path.curdir, 'simplehttp', 'download','example')
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
        
        
if __name__ == "__main__": # must run this from root dir or it won't work

    handler = SimpleFileHandler
    ip = utils.get_ip()

    with socketserver.TCPServer((ip,consts.PORT), handler) as httpd:
        print("serving at port", consts.PORT)
        print("serving at address", ip)
        httpd.serve_forever()
