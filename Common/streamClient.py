# client.py

import socket
# from socket import SOL_SOCKET, SO_TYPE
# ip = '<broadcast>'
myIP = socket.gethostbyname(socket.gethostname())
print(myIP)
# ip = "127.0.0.1"

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
# soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
clients_input = input("What you want to send my dear client?\n")  
soc.connect((myIP, 53078))



soc.send(clients_input.encode("utf8")) # we must encode the string to bytes  
result_bytes = soc.recv(4096) # the number means how the response can be in bytes  
result_string = result_bytes.decode("utf8") # the return will be in bytes, so decode

print("Result from server is {}".format(result_string))  