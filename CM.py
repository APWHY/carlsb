from common import cryptostuff,packers,peerBase
from common import consts,handlers
import socketserver, socket,_thread
from threading import Thread

# The assumption for now is that CM's only ever communicate with CH's and vice versa.

# Handles UDP requests for a CM -- should only recieve IntroMsg
class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0] #.strip()
        usingSocket = self.request[1]
        print("{}:{}@CMUDP wrote: ".format(self.client_address[0],self.client_address[1]))
        # print(data)
        print("received by : {}:{}".format(usingSocket.getsockname()[0],usingSocket.getsockname()[1])) #gets my own address/port pair
        print()
        unpacked = None

        for unpack in [packers.IntroMsg.ungenMsg(data)]:
            unpacked = unpack # should only recieve IntroMsg 
            if unpacked != None: # we have recieved a msg
                if unpacked.msgType == consts.MSG_INTRO and unpacked.nodeType == consts.TYPE_CH: #sanity check -- might need code for more than IntroMsg and we only care about IntroMsg from CHs...who should be the only ones sending them
                    rootNode = self.server.CM
                    rootNode.lock.acquire() # Critical region
                    rootNode.CH.populate(unpacked.IP,unpacked.port,unpacked.key)
                    rootNode.lock.release() # End critical region
                    rootNode.ackCH(unpacked.msgType)
                    break #we can leave the for loop now
                else:
                    pass #for now we pass but for future message types we handle them here

# Handles TCP requests for a CM -- should not actually revieve anything and is just a stub
class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("{}:{}@CMTCP wrote: ".format(self.client_address[0],self.client_address[1]))
        print(self.data)
        print("received by : {}:{}".format(self.request.getsockname()[0],self.request.getsockname()[1])) #gets my own address/port pair
        print()
        self.request.sendall(self.data.upper())




class ClusterHeadRep():
    def __init__(self):
        self.exists = False
    
    def populate(self,ip,port,publicKey):
        self.exists = True
        self.IP = ip
        self.port = port 
        self.publicKey = publicKey
        #perhaps have a ttl for this but whatever

    def depopulate(self):
        self.exists = False


# Threading issues here... going ot have to make CM CH threadsafe
# Deal with passing CM/CH object (it is mutable so you can pass by reference) to __init__
# Need to override the __init__ function of BaseRequestHandler to do this
# Then the handlers can modify the state of the CM/CH and do stuff normally



class ClusterMember(peerBase.commonNode):

        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs) #do standard commonNode stuff
            
            self.lock = _thread.allocate_lock() # for modifications to self.CH and self.privateKey
            self.streamServer.CM = self # pass reference to self to the stream and broadcast servers so the handlers can modify the state of the CM based on messages received
            self.broadcastServer.CM = self
            self.privateKey = cryptostuff.newPrivateKey()
            self.publicKey = self.privateKey.public_key()
            self.CH = ClusterHeadRep()

            super().hold()
            print("CM serving")

        # sending an ack is very simple -- assumption is that acks always go to a CH
        def ackCH(self,ackType):
            if self.CH.exists:
                print("sending ACK to port: " + str(self.CH.port) + " and ip: "+ self.CH.IP)
                msg = packers.AckMsg(consts.TYPE_CM,self.IP,self.SSERVPORT,ackType,self.publicKey).genMsg()
                super().sendTCP(msg,self.CH.IP,self.CH.port)
        
        def verifyTransaction(self):
            pass
            # TODO