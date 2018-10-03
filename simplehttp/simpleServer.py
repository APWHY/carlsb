import http.server
import socketserver
import socket
import os
import shutil

PORT = 8088

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class HTTPHandlerOne(http.server.BaseHTTPRequestHandler):
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
        
        


Handler = HTTPHandlerOne


with socketserver.TCPServer(("",PORT), Handler) as httpd:
    print("serving at port", PORT)
    print("serving at address", get_ip())
    httpd.serve_forever()
