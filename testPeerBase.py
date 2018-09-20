from common.peerBase import commonNode 
from common import consts, handlers
import socket
from threading import Thread
import time

# python's import system tilts me to no end

def id(thing):
    return thing

def sendTCP(msg, ip, port):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    # soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 
    # print(port) 
    soc.connect((ip,port))
    soc.send(msg.encode("utf8")) # we must encode the string to bytes  
    result_bytes = soc.recv(4096)   
    result_string = result_bytes.decode("utf8") # the return will be in bytes, so decode

    return result_string

def broadcast(msg):
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
    soc.sendto(msg.encode("utf8"), (('<broadcast>',consts.BROADCAST_PORT)))
    result_bytes, _ = soc.recvfrom(4096) 
    result_string = result_bytes.decode("utf8") # the return will be in bytes, so decode
    return result_string



def testTCPServerReceives(first):
    testString = "Example piece of text that should become uppercase"

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    soc.connect((first.IP,first.SSERVPORT ))
    soc.send(testString.encode("utf8")) # we must encode the string to bytes  
    result_bytes = soc.recv(4096)   
    result_string = result_bytes.decode("utf8") # the return will be in bytes, so decod

    assert(testString.upper() == result_string)

def testUDPServerReceivesBroadcast(first):
    testString = "Some other piece of text that also becomes uppercase"
    recvString = broadcast(testString)
    assert(testString.upper() == recvString)

def testSendsTCP(first):
    # create a simple TCP server to listen for TCP transmissions from our node
    ip = socket.gethostbyname(socket.gethostname())
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind((ip,0))
    soc.listen(10)
    # make a TCP transmission
    testString = "new message incoming!"
    Thread(target=first.sendTCP, args=(testString,ip,soc.getsockname()[1]), daemon=True).start()
    # normally you would handle this in a seperate thread but since we're only testing one conn it's fine
    conn, addr = soc.accept()
    ip, _ = str(addr[0]), str(addr[1])
    res = conn.recv(4096)
    conn.sendall("ack".encode("utf8"))
    conn.close()
    soc.close()
    assert(testString == res.decode("utf8"))

def testSendsBroadcast(first):
    # create a simple udp server to listen for the transmission
    ip = socket.gethostbyname(socket.gethostname())
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind((ip,consts.BROADCAST_PORT))
    testString = b"your tax is due in october"

    Thread(target=first.broadcast, args=(testString,), daemon=True).start() # need the comma or Thread thinks testString is a list of chars
    data , _ = soc.recvfrom(4096)
    assert(testString == data) 
    # note that first and second recieve this message as well because of the nature of broadcasts

if __name__ == "__main__":    
    first = commonNode(handlers.simpleUDPHandler,handlers.simpleTCPHandler) 
    second = commonNode(handlers.simpleUDPHandler,handlers.simpleTCPHandler) 
    # print("found streaming server port is : " + str(first.SSERVPORT))
    first.hold()
    second.hold()
    testTCPServerReceives(second)
    testUDPServerReceivesBroadcast(first)
    testSendsTCP(first)
    testSendsBroadcast(first)

    time.sleep(3) # needed or the daemon threads trying to print will fry themselves
    # eventually i'll remove the print and that won't be an issue anymore




