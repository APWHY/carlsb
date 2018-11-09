# simple client to send udp broadcasts from
# only purpose is to test functionality manually
import socket


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

soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
soc.bind((get_ip(),12346))

clients_input = input("What you want to broadcast, my dear client?\n")  

soc.sendto(clients_input.encode("utf8"), (('<broadcast>',28196)))
