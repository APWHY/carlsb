import socketserver,socket

# This file contains handlers for TCP and UDP requests
# Likely not used in the project except for testing purposes



# simple handler for TCP requests which makes things uppercase
class simpleTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("{}:{}@simpleTCP wrote: ".format(self.client_address[0],self.client_address[1]))
        print(self.data)
        print("received by : {}:{}".format(self.request.getsockname()[0],self.request.getsockname()[1])) #gets my own address/port pair
        print()
        self.request.sendall(self.data.upper())

# simple handler for UDP request which makes things uppercase
class simpleUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        usingSocket = self.request[1]
        print("{}:{}@simpleUDP wrote: ".format(self.client_address[0],self.client_address[1]))
        print(data)
        # print(usingSocket.getsockname()) #gets my own address/port pair
        print("received by : {}:{}".format(usingSocket.getsockname()[0],usingSocket.getsockname()[1])) #gets my own address/port pair
        print()
        usingSocket.sendto(data.upper(), self.client_address)