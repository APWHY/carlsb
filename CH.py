from common import cryptostuff,peerBase,packers,consts, utils, contractCaller
import socketserver, socket,_thread, collections

# The assumption for now is that CM's only ever communicate with CH's and vice versa.

# Handles UDP requests for a CH -- should not receive anything honestly
# For now we assume that CHs are the ones that advertise themselves and a CM is always going to be in the vicinity of a CH
class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0]#.strip()
        usingSocket = self.request[1]
        print("{}:{}@CHUDP wrote: ".format(self.client_address[0],self.client_address[1]))
        print(data)
        print("received by : {}:{}".format(usingSocket.getsockname()[0],usingSocket.getsockname()[1])) #gets my own address/port pair
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
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
                    print("adding new CM")
                    rootNode.lock.acquire() # Critical region
                    rootNode.newCM(unpacked.IP,unpacked.port,unpacked.key)
                    rootNode.lock.release() # End critical region
                    break
                if unpacked.msgType == consts.MSG_TRANS and unpacked.nodeType == consts.TYPE_CM and rootNode.checkCM(unpack.key):
                    rootNode.sendTransaction(unpack.key,unpack.signature) 
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

        self.rebroadcaster = utils.job(self.broadcastIntro,consts.BROADCAST_FREQ) #responsible for periodically calling broadcastIntro
    
        super().hold()
        self.rebroadcaster.start()
        
        print("CH serving")

    # Adds a new CM to the list of CM's the CH knows exists if it isn't already on the list
    # TODO clean out the list every once in a while
    def newCM(self, ip,port,pubKey):
        print("trying to add new CM")
        if not self.checkCM(pubKey)[0]:
            print("actually adding new cm")
            self.CMs.append(ClusterMemberRep(ip,port,pubKey))

    def checkCM(self,pubKey):
        for d in self.CMs:
            if d.pubKey.public_numbers().n == pubKey.public_numbers().n:
                return True, d
        return False, None

    # helper function -- should be called periodically
    def broadcastIntro(self):
        print("CH sending broadcast...")
        super().broadcast(packers.IntroMsg(consts.TYPE_CH,self.IP,self.SSERVPORT,self.pubKey).genMsg())

    def sendTransaction(self, pubKey, sig):
        check,sender = self.checkCM(pubKey)
        print("-------------------")
        print("result of check is:")
        print(check)
        print(len(self.CMs))
        if not check:

            for d in self.CMs:
                print("in CMs")
                print(d.pubKey.public_numbers())
            print(pubKey.public_numbers(),sig)
            raise AssertionError("Attempt to send transaction from unregistered CM")

        print("appending CM transaction to blockchain...")
        # I store the public Key as string because I ran into problems with dynamic byte arrays in dicts for solidity
        # That may have been due to another issue which has since been resolved since this decision was made fairly early on
        pubKeyBytes = cryptostuff.keyToBytes(pubKey)
        print(pubKeyBytes)
        # print(sig)
        # sigStr = sig.decode(consts.ENCODE_SIG)
        if sender.contract == "":
            sender.contract = self.manager.addNode(pubKeyBytes,sig)
        else:
            self.manager.checkMsg(pubKeyBytes,sig)

        print("CM transaction appeneded to blockchain, notifying CM now...")
        print(packers.TransMsg.ungenMsg(packers.TransMsg(consts.TYPE_CH,sig,self.pubKey).genMsg()))
        print(packers.TransMsg(consts.TYPE_CH,sig,self.pubKey).genMsg())
        print(len(packers.TransMsg(consts.TYPE_CH,sig,self.pubKey).genMsg()))
        super().sendTCP(packers.TransMsg(consts.TYPE_CH,sig,self.pubKey).genMsg(),sender.IP,sender.port)

    # only checks if the source of pubKey has actually put up sig on the blockchain
    # verification of signature with message should be done elsewhere
    def verifyTransaction(self, pubKey, sig):
        check,sender = self.checkCM(pubKey)
        if check:
            contractAddr = sender.address
        else:
            contractAddr = self.manager.getNode(cryptostuff.keyToBytes(pubKey))
        if sender == 0:
            return False
        return self.manager.checkMsg(contractAddr, sig)

