from common import cryptostuff,peerBase,packers,consts, repeatable, contractCaller
import socketserver, socket,_thread, collections

# The assumption for now is that CM's only ever communicate with CH's and vice versa.

# Handles UDP requests for a CH -- should not receive anything honestly
# For now we assume that CHs are the ones that advertise themselves and a CM is always going to be in the vicinity of a CH
class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        _ = data #delete this TODO
        usingSocket = self.request[1]
        print("{}:{}@CHUDP wrote: ".format(self.client_address[0],self.client_address[1]))
        # print(data)
        print("received by : {}:{}".format(usingSocket.getsockname()[0],usingSocket.getsockname()[1])) #gets my own address/port pair
        print()
        unpacked = None

        for unpack in []: # stub code for future work
            unpacked = unpack  
            if unpacked != None: # we have recieved a msg
                pass

# Handles TCP requests for a CH -- should not actually recieve anything and is just a stub
class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024) # .strip()
        print(len(self.data))
        print("{}:{}@CMTCP wrote: ".format(self.client_address[0],self.client_address[1]))
        print(self.data)
        print("received by : {}:{}".format(self.request.getsockname()[0],self.request.getsockname()[1])) #gets my own address/port pair
        print()
        unpacked = None

        for unpack in [packers.AckMsg.ungenMsg(self.data),packers.TransMsg.ungenMsg(self.data)]:
            unpacked = unpack
            if unpacked != None:
                rootNode = self.server.CH
                if unpacked.msgType == consts.MSG_ACK and unpacked.nodeType == consts.TYPE_CM:
                    rootNode.lock.acquire() # Critical region
                    rootNode.newCM(unpacked.IP,unpacked.port,unpacked.key)
                    rootNode.lock.release() # End critical region
                    break
                if unpacked.msgType == consts.MSG_TRANS and unpacked.nodeType == consts.TYPE_CM and rootNode.checkCM(unpack.key):
                    rootNode.sendTransaction() 
                    break
                else:
                    pass # add other stuff later


class ClusterMemberRep():
    def __init__(self,ip,port,pubKey):
        self.IP = ip
        self.port = port 
        self.pubKey = pubKey
        self.contract = ""
        #perhaps have a ttl for this but whatever

class ClusterHead(peerBase.commonNode):
     
    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)  # standard commonNode setup

        self.manager  = contractCaller.ContractManager()
        
            

        self.lock = _thread.allocate_lock() # for modifications to self.CMs
        self.streamServer.CH = self # pass reference to self to the stream and broadcast servers so the handlers can modify the state of the CM based on messages received
        self.broadcastServer.CH = self # This hurts having last worked in go and haskell lmao
        self.privateKey = cryptostuff.newPrivateKey()
        self.pubKey = self.privateKey.public_key()
        self.CMs = collections.deque()

        self.rebroadcaster = repeatable.job(self.broadcastIntro,consts.BROADCAST_FREQ) #responsible for periodically calling broadcastIntro
    
        super().hold()
        self.rebroadcaster.start()
        
        print("CH serving")

    # Adds a new CM to the list of CM's the CH knows exists if it isn't already on the list
    # TODO clean out the list every once in a while
    def newCM(self, ip,port,pubKey):
        if self.checkCM(pubKey)[0]:
            self.CMs.append(ClusterMemberRep(ip,port,pubKey))

    def checkCM(self,pubKey):
        for d in self.CMs:
            if d.pubKey == pubKey:
                return True, d
        return False, None

    # helper function -- should be called periodically
    def broadcastIntro(self):
        print("CH sending broadcast...")
        super().broadcast(packers.IntroMsg(consts.TYPE_CH,self.IP,self.SSERVPORT,self.pubKey).genMsg())

    def sendTransaction(self, pubKey, sig):
        check,sender = self.checkCM(pubKey)
        if not check:
            import json
            print(json.dumps(self.CMs))
            print(pubKey,sig)
            raise AssertionError("Attempt to send transaction from unregistered CM")

        print("appending CM transaction to blockchain...")
        if sender.address == "":
            sender.address = self.manager.addNode(pubKey,sig)
        else:
            self.manager.checkMsg(pubKey,sig)

        print("CM transaction appeneded to blockchain, notifying CM now...")
        super().sendTCP(packers.TransMsg(consts.TYPE_CH,sig,self.pubKey).genMsg(),sender.ip,sender.port)

    # only checks if the source of pubKey has actually put up sig on the blockchain
    # verification of signature with message should be done elsewhere
    def verifyTransaction(self, pubKey, sig):
        sender = self.manager.getNode(pubKey)
        if sender == 0:
            return False
        return self.manager.checkMsg(sender, sig)

