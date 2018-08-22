import socketserver,socket

class MYUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        usingSocket = self.request[1]
        print("{}:{} wrote: ".format(self.client_address[0],self.client_address[1]))
        print(data)
        print(usingSocket.getsockname()) #gets my own address/port pair
        usingSocket.sendto(data.upper(), self.client_address)

myIP = socket.gethostbyname(socket.gethostname())
print(myIP)
bserver = socketserver.UDPServer((myIP,0), MYUDPHandler )
print(bserver.socket.getsockname())
bserver.serve_forever()