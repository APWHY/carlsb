from common import cryptostuff,packers,peerBase,consts,handlers,msgEvent 
import socketserver, socket,_thread
from threading import Thread

# The assumption for now is that CM's only ever communicate with CH's and vice versa.

# Handles UDP requests for a CM -- should only recieve IntroMsg
class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0] #.strip()
        # usingSocket = self.request[1]
        # print("{}:{}@CMUDP wrote: ".format(self.client_address[0],self.client_address[1]))
        # print(data)
        # print("received by : {}:{}".format(usingSocket.getsockname()[0],usingSocket.getsockname()[1])) #gets my own address/port pair
        # print()
        unpacked = None

        for unpack in [packers.IntroMsg.ungenMsg(data), packers.MsgMsg.ungenMsg(data)]:
            unpacked = unpack # should only recieve IntroMsg 
            if unpacked != None: # we have recieved a msg
                rootNode = self.server.CM
                if unpacked.msgType == consts.MSG_INTRO and unpacked.nodeType == consts.TYPE_CH: #sanity check -- might need code for more than IntroMsg and we only care about IntroMsg from CHs...who should be the only ones sending them
                    rootNode.lock.acquire() # Critical region
                    filled = rootNode.CH.populate(unpacked.IP,unpacked.port,unpacked.key)
                    rootNode.lock.release() # End critical region
                    if not filled: #only bother sending ack if we haven't already sent one
                        rootNode.ackCH(unpacked.msgType)
                    break #we can leave the for loop now
                if unpacked.msgType == consts.MSG_MSG and unpacked.nodeType == consts.TYPE_CM and rootNode.hasDownload:
                        rootNode.downloadFunc(unpacked.IP,unpacked.port,unpacked.signature,unpacked.key)
                else:
                    pass #for now we pass but for future message types we handle them here

# Handles TCP requests for a CM -- should only be receiving acknowledgment TRANS_MSGs from CHs
class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(consts.RECV_SIZE)# .strip()
        # print("{}:{}@CMTCP wrote: ".format(self.client_address[0],self.client_address[1]))
        # print(self.data)
        # print("received by : {}:{}".format(self.request.getsockname()[0],self.request.getsockname()[1])) #gets my own address/port pair
        # print()
        # print("~?~?~?~?~?~?~?~~?~?~??~?~?~?~~??~?~?~?~?~~??~~?~?~?")
        for unpack in [packers.TransMsg.ungenMsg(self.data),packers.VerifyMsg.ungenMsg(self.data)]:
            unpacked = unpack # should only recieve TransMsg 
            print(unpacked)
            if unpacked != None: # we have recieved a msg
                rootNode = self.server.CM
                if unpacked.msgType == consts.MSG_TRANS and unpacked.nodeType == consts.TYPE_CH and unpacked.key.public_numbers().n == rootNode.CH.pubKey.public_numbers().n: #sanity check -- might need code for more than IntroMsg and we only care about IntroMsg from CHs...who should be the only ones sending them
                    # print("confirmation of transaction received")
                    rootNode.holdMsgs(unpacked.signature)
                    break # we can leave the loop now
                if unpacked.msgType == consts.MSG_VERIFY and unpacked.nodeType == consts.TYPE_CH and unpacked.keySender.public_numbers().n == rootNode.CH.pubKey.public_numbers().n:
                    # print("verification response received -- excuting handler now")
                    rootNode.holdMsgs(unpacked.signature,unpacked.result)
                    break # we can leave the loop now
                else:
                    pass # for now we pass but for future message types we handle them here

class CHDoesNotExist(Exception):
    pass


class ClusterHeadRep():
    def __init__(self):
        self.exists = False
    
    def populate(self,ip,port,pubKey):
        res = self.exists
        self.exists = True
        self.IP = ip
        self.port = port 
        self.pubKey = pubKey
        return res
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
            self.broadcastServer.CM = self # bit naughty to do this but beats having another layer of inheritance (and I think it's pythonic anyway to do this?)
            self.privateKey = cryptostuff.newPrivateKey()
            self.pubKey = self.privateKey.public_key()
            self.CH = ClusterHeadRep()
            self.holdMsgs = msgEvent.MsgEvent()
            self.hasDownload = False
            super().hold()
            print("CM is up")


        def addDownloadFunc(self, downloadFunc):
            self.hasDownload = True
            self.downloadFunc = downloadFunc

        def sendCH(self,msg):
            super().sendTCP(msg,self.CH.IP,self.CH.port)

        # sending an ack is very simple -- assumption is that acks always go to a CH
        def ackCH(self,ackType):
            if self.CH.exists:
                # print("sending ACK to port: " + str(self.CH.port) + " and ip: "+ self.CH.IP)
                msg = packers.AckMsg(consts.TYPE_CM,self.IP,self.SSERVPORT,ackType,self.pubKey).genMsg()
                self.sendCH(msg)
            else:
                raise CHDoesNotExist("This CM is not connected to a CH and cannot execute this function as a result")
            
        

        # Sends the signature of the message off to the CH to be appended to the blockchain
        # The handler is executed when the TRANS_MSG is recieved back at the CM
        
        # The handler is expected to have signature handler()
        def sendTransaction(self, handler, sig):
            if self.CH.exists:
                self.holdMsgs[sig] = handler
                # print("sending transaction off to CH to be appended to blockchain")
                self.sendCH(packers.TransMsg(consts.TYPE_CM,sig,self.pubKey).genMsg())
            else:
                raise CHDoesNotExist("This CM is not connected to a CH and cannot execute this function as a result")
        
        # This does not check the quality of the signature, merely whether or not it is in the blockchain
        # cryptostuff.verifymsg should be called from elsewhere (preferably before calling this function)
        # Actually just forwards all the info to the CH for it to do the work
        # Perhaps in the future we can give CM's access to the blockchain but I feel it is somewhat overkill to do so
        
        # The handler is expected to have signature handler(bool)
        def verifyTransaction(self, handler, pubKey, sig):
            if self.CH.exists:
                self.holdMsgs[sig] = handler
                # print("checking signature is in blockchain")
                print(len(packers.VerifyMsg(consts.TYPE_CM,sig,pubKey,self.pubKey,False).genMsg()))
                self.sendCH(packers.VerifyMsg(consts.TYPE_CM,sig,pubKey,self.pubKey,False).genMsg())
            else:
                raise CHDoesNotExist("This CM is not connected to a CH and cannot execute this function as a result")

