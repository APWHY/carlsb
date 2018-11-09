# Contains the CM class and all relevant classes to it
from common import cryptostuff,packers,peerBase,consts,handlers,msgEvent,utils 
import socketserver, socket,_thread
from threading import Thread

# The assumption for now is that CM's only ever communicate with CH's and vice versa.

# Handles UDP requests for a CM -- should only recieve IntroMsg
class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0] 

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

# Handles TCP requests for a CM
class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(consts.RECV_SIZE)# .strip()

        for unpack in [packers.TransMsg.ungenMsg(self.data),packers.VerifyMsg.ungenMsg(self.data)]:
            unpacked = unpack # should only recieve TransMsg or VerifyMsg
            if unpacked != None: # we have recieved a msg
                rootNode = self.server.CM
                if unpacked.msgType == consts.MSG_TRANS and unpacked.nodeType == consts.TYPE_CH and unpacked.key.public_numbers().n == rootNode.CH.pubKey.public_numbers().n: #sanity check -- might need code for more than IntroMsg and we only care about IntroMsg from CHs...who should be the only ones sending them
                    rootNode.holdMsgs(unpacked.signature)
                    break 
                if unpacked.msgType == consts.MSG_VERIFY and unpacked.nodeType == consts.TYPE_CH and unpacked.keySender.public_numbers().n == rootNode.CH.pubKey.public_numbers().n:
                    rootNode.holdMsgs(unpacked.signature,unpacked.result)
                    break
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

    def depopulate(self):
        self.exists = False

# The CM is responsible for taking a message from... somewhere and passing it on to the CH to get it added to the blockchain
# Alternatively, it has a signature and public key pair which it passes to the CH so the CH can ensure that the pairing is legitimate
class ClusterMember(peerBase.commonNode):

        def __init__(self,*args,hasKUI=False,**kwargs):
            super().__init__(*args,**kwargs) #do standard commonNode stuff
            
            self.lock = _thread.allocate_lock() # for modifications to self.CH and self.privateKey
            self.streamServer.CM = self # pass reference to self to the stream and broadcast servers so the handlers can modify the state of the CM based on messages received
            self.broadcastServer.CM = self # bit naughty to do this but beats having another layer of inheritance (and I think it's pythonic anyway to do this?)
            self.privateKey = cryptostuff.newPrivateKey()
            self.pubKey = self.privateKey.public_key()
            self.CH = ClusterHeadRep()
            self.holdMsgs = msgEvent.MsgEvent()
            self.hasDownload = False
            self.hasKUI = hasKUI
            
            self.hold()
            self.KUI = utils.job(self.KUICH, consts.KUI_INTERVAL)
            self.KUI.start()

        # This is a helper function for the demo.
        # The downloadFunc executes when a MSG_MSG is received by the CM
        # In reality this should not happen in the CM but outside but it requires an external 'network' to be set up
        def addDownloadFunc(self, downloadFunc):
            self.hasDownload = True
            self.downloadFunc = downloadFunc

        # Wrapper for the super sendTCP function
        def sendCH(self,msg):
            self.sendTCP(msg,self.CH.IP,self.CH.port)

        # sending an ack is very simple -- assumption is that acks always go to a CH
        def ackCH(self,ackType):
            if self.CH.exists:
                msg = packers.AckMsg(consts.TYPE_CM,self.IP,self.SSERVPORT,ackType,self.pubKey).genMsg()
                self.sendCH(msg)
            else:
                raise CHDoesNotExist("This CM is not connected to a CH and cannot execute this function as a result")
        # sends a KUI_MSG to a CH after changing the public-private key pair (if needed)    
        def KUICH(self):
            if not self.CH.exists: # dont send this if there is no CH
                return
            oldPub = self.pubKey
            if self.hasKUI:
                self.privateKey = cryptostuff.newPrivateKey()
                self.pubKey = self.privateKey.public_key() 
            msg = packers.KUIMsg(consts.TYPE_CM,oldPub,self.pubKey).genMsg()
            self.sendCH(msg)

        # Sends the signature of the message off to the CH to be appended to the blockchain
        # The handler is executed when the TRANS_MSG is recieved back at the CM
        # The handler is expected to have signature handler()
        def sendTransaction(self, handler, sig):
            if self.CH.exists:
                self.holdMsgs[sig] = handler
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
                self.sendCH(packers.VerifyMsg(consts.TYPE_CM,sig,pubKey,self.pubKey,False).genMsg())
            else:
                raise CHDoesNotExist("This CM is not connected to a CH and cannot execute this function as a result")

