# Contains the CH class and all relevant classes to it
from common import cryptostuff,peerBase,packers,consts, utils, contractCaller
import socketserver, socket,_thread, collections,time

# The assumption for now is that CM's only ever communicate with CH's and vice versa.

# Handles UDP requests for a CH -- should not receive anything honestly and is a stub at the moment
# For now we assume that CHs are the ones that advertise themselves and a CM is always going to be in the vicinity of a CH
class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # data = self.request[0]
        # usingSocket = self.request[1]
        unpacked = None
        for unpack in []: # stub code for future work
            unpacked = unpack  
            if unpacked != None: # we have recieved a msg
                pass

# Handles TCP requests for a CH 
class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(consts.RECV_SIZE)
        unpacked = None
        # We figure out the type of the message by trying all of the unpack functions in packers
        # Eventually one will work (if it doesnt we discard the message) and we can go to a 'switch' statement
        # Except python doesn't have one so we just have a billion if statements
        for unpack in [packers.AckMsg.ungenMsg(self.data),packers.TransMsg.ungenMsg(self.data),packers.VerifyMsg.ungenMsg(self.data),packers.KUIMsg.ungenMsg(self.data)]:
            unpacked = unpack
            if unpacked != None:
                rootNode = self.server.CH
                if unpacked.msgType == consts.MSG_ACK and unpacked.nodeType == consts.TYPE_CM:
                    rootNode.lock.acquire() # Critical region
                    rootNode.newCM(unpacked.IP,unpacked.port,unpacked.key) # Add a new CM to our list of CMs
                    rootNode.lock.release() # End critical region
                    break
                if unpacked.msgType == consts.MSG_TRANS and unpacked.nodeType == consts.TYPE_CM and rootNode.checkCM(unpack.key):
                    rootNode.sendTransaction(unpack.key,unpack.signature) 
                    break
                if unpacked.msgType == consts.MSG_VERIFY and unpacked.nodeType == consts.TYPE_CM:
                    rootNode.verifyTransaction(unpacked.keyTransSender,unpacked.keySender,unpacked.signature)               
                if unpacked.msgType == consts.MSG_KUI and unpacked.nodeType == consts.TYPE_CM:
                    rootNode.lock.acquire() # Critical region
                    res,old = rootNode.checkCM(unpack.keyOld)
                    if res: # If the sender already exists in our list of CMs, we make a new entry for the sender.
                            # Otherwise we ignore it so malicious attackers cannot insert themselves into
                            # the network through this way         
                        rootNode.newCM(old.IP,old.port,unpacked.keyNew)
                    rootNode.lock.release() # End critical region
                    break
                else:
                    pass # add other stuff later


class ClusterMemberRep():
    def __init__(self,ip,port,pubKey):
        self.IP = ip
        self.port = port 
        self.pubKey = pubKey
        self.contract = ""
        self.start = time.clock()
# The CH class is responsible for facilitating communications between a CM and the ledger managing the network
# It also keeps track of which CMs it is currently connected to
class ClusterHead(peerBase.commonNode):
     
    def __init__(self,*args,spoofContract=False,**kwargs):

        super().__init__(*args,**kwargs)  # standard commonNode setup
        if spoofContract:
            self.manager = contractCaller.ContractManagerSpoof()
        else:
            self.manager  = contractCaller.ContractManager()
        
            

        self.lock = _thread.allocate_lock() # for modifications to self.CMs
        self.streamServer.CH = self # pass reference to self to the stream and broadcast servers so the handlers can modify the state of the CM based on messages received
        self.broadcastServer.CH = self # This hurts having last worked in go and haskell lmao
        self.privateKey = cryptostuff.newPrivateKey()
        self.pubKey = self.privateKey.public_key()
        self.CMs = collections.deque()

        self.rebroadcaster = utils.job(self.broadcastIntro,consts.BROADCAST_FREQ) # responsible for periodically calling broadcastIntro
        self.KUIclean = utils.job(self.clearCMs, consts.KUI_INTERVAL) # responsible for keeping the CMs list clear of old entries
        self.hold()
        self.rebroadcaster.start()
        self.KUIclean.start()


    # Adds a new CM to the list of CM's the CH knows exists if it isn't already on the list
    def newCM(self, ip,port,pubKey):
        self.CMs.append(ClusterMemberRep(ip,port,pubKey))

    # Checks whether or not a CM is in the list and returns it if it is
    def checkCM(self,pubKey):
        for d in self.CMs:
            if d.pubKey.public_numbers().n == pubKey.public_numbers().n:
                return True, d
        return False, None

    # helper function to clear out old CMs -- called periodically through the job utility
    def clearCMs(self):
        now = time.clock()
        newCMs = []
        self.lock.acquire()
        for d in self.CMs:
            if (now - d.start) < 2*consts.KUI_INTERVAL:
                newCMs.append(d)
        self.CMs = newCMs
        self.lock.release()

    # helper function to send the MSG_INTRO broadcast -- should be called periodically
    def broadcastIntro(self):
        self.broadcast(packers.IntroMsg(consts.TYPE_CH,self.IP,self.SSERVPORT,self.pubKey).genMsg())

    # Calls the addNode or postMsg functions in the ContractManager interface
    # Also keeps track of which CMs already have an Individual contract bound to them
    def sendTransaction(self, pubKey, sig):
        check,sender = self.checkCM(pubKey)
        if not check:
            for d in self.CMs:
                print(d.pubKey.public_numbers())
            print(pubKey.public_numbers(),sig)
            raise AssertionError("Attempt to send transaction from unregistered CM")

       
        # I store the public Key as string because I ran into problems with dynamic byte arrays in dicts for solidity
        # That may have been due to another issue which has since been resolved since this decision was made fairly early on
        pubKeyBytes = cryptostuff.keyToBytes(pubKey)

        if sender.contract == "": # The CM doesn't have an Individual contract yet
            self.manager.addNode(pubKeyBytes,sig)
            sender.contract = self.manager.getNode(pubKeyBytes)
        else:
            self.manager.postMsg(sender.contract,sig)
            
        self.sendTCP(packers.TransMsg(consts.TYPE_CH,sig,self.pubKey).genMsg(),sender.IP,sender.port)

    # only checks if the source of pubKey has actually put up sig on the blockchain
    # verification of signature with message should be done elsewhere
    def verifyTransaction(self, pubKeyTransSender, pubKeySender, sig):
        check,sender = self.checkCM(pubKeySender)
        if not check:
            raise AssertionError("This user doesn't exist")
    
        check,transSender = self.checkCM(pubKeyTransSender)
        if check:
            contractAddr = transSender.contract
        else:
            contractAddr = self.manager.getNode(cryptostuff.keyToBytes(pubKeyTransSender))
        if sender == 0:
            res = False
 
        res =  self.manager.checkMsg(contractAddr, sig)
        msg = packers.VerifyMsg(consts.TYPE_CH,sig,pubKeyTransSender,self.pubKey,res).genMsg()
        self.sendTCP(msg,sender.IP,sender.port)

