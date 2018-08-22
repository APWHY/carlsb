import socketserver,socket

class MYTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("{}:{} wrote: ".format(self.client_address[0],self.client_address[1]))
        print(self.data)
        print(self.request.getsockname()) #gets my own address/port pair
        self.request.sendall(self.data.upper())

myIP = socket.gethostbyname(socket.gethostname())
print(myIP)
sserver = socketserver.TCPServer((myIP,0), MYTCPHandler )
print(sserver.socket.getsockname())
sserver.serve_forever()