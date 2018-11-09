# simple client to send TCP messages from
# only used as a tool for manual testing

import socket

# ip = '<broadcast>'
myIP = socket.gethostbyname(socket.gethostname())
print(myIP)
# ip = "127.0.0.1"

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
# soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
clients_input = input("What you want to send my dear client?\n")  
soc.connect((myIP, 54373))

soc.send(clients_input.encode("utf8"))
result_bytes = soc.recv(4096)  
result_string = result_bytes.decode("utf8") 

print("Result from server is {}".format(result_string))  