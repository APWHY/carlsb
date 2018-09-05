import commonConstants,cryptostuff
import struct

# This file contains all the message classes used in the project
# They all implement a simple interface and are used to serialise important information
# That nodes want to send to each other (and unpack them as well)


# IntroMsg -- for a node to inform another node of its existence
# always sent on the broadcast channel
# contains 5 things:
    # 1. Message type (MSG_INTRO)
    # 2. Node type (whether the sender is a CH or CM as an int)
    # 3. IP address of sender (assumed to be a string)
    # 4. Port number of sender (assumed to be an int)
    # 5. The public key of the sender (assumed to be a cryptography.hazmat.backends.openssl.rsa.RSAPublicKey type)
class IntroMsg:

    fmt = struct.Struct(commonConstants.MSG_INTRO_FMT) # the specific format of how we plan on serialising our struct
    
    msgType = commonConstants.MSG_INTRO
    def __init__(self, nodeType, ip, port,key):
        self.nodeType = nodeType
        self.IP = ip
        self.port = port
        self.key = key # this should be a public key


    # genMsg -- Takes an IntroMsg object and seralises it into bytes for sending over a network
    def genMsg(self):
        values = (
            self.msgType,
            self.nodeType,
            bytes(self.IP,'utf-8'),
            self.port,
            cryptostuff.keyToBytes(self.key)
        )
        return self.fmt.pack(*values) # splat


    # The below method is static because we want to call it without an instance of IntroMsg
    # We can think of it as an alternative constructor (if you're into Java)  
    #  
    # ungenMsg -- takes a serialised IntroMsg and returns a IntroMsg with all types correctly set
    # If not given a bytes object with IntroMsg.fmt's formatting, returns TypeError
    @staticmethod
    def ungenMsg(data):
        opened = IntroMsg.fmt.unpack(data)
        if opened[0] == IntroMsg.msgType:
            raw = IntroMsg.fmt.unpack(data)
            retVal = IntroMsg(*raw[1:])
            retVal.IP = retVal.IP.decode('utf-8').replace("\x00",'') # remove null chars at the end of the string
            retVal.key = cryptostuff.bytesToKey(retVal.key)
            return retVal
        else:
            raise TypeError



# TransMsg -- for a CM to send a transaction to a CH
    # always sent via TCP
    # contains 4 things:
        # 1. Message type (MSG_TRANS)
        # 2. Node type (whether the sender is a CH or CM as an int)
        # 3. Signature of the message being sent (256 bytes)
        # 4. The public key of the sender (assumed to be a cryptography.hazmat.backends.openssl.rsa.RSAPublicKey type)
class TransMsg:

    fmt = struct.Struct(commonConstants.MSG_TRANS_FMT) # the specific format of how we plan on serialising our struct
    
    msgType = commonConstants.MSG_TRANS
    def __init__(self, nodeType, signature,key):
        self.nodeType = nodeType
        self.signature = signature
        self.key = key # this should be a public key


    # genMsg -- Takes a TransMsg object and seralises it into bytes for sending over a network
    def genMsg(self):
        values = (
            self.msgType,
            self.nodeType,
            self.signature,
            cryptostuff.keyToBytes(self.key)
        )
        return self.fmt.pack(*values) # splat


    # The below method is static because we want to call it without an instance of TransMsg
    # We can think of it as an alternative constructor (if you're into Java)  
    #  
    # ungenMsg -- takes a serialised TransMsg and returns a TransMsg with all types correctly set
    # If not given a bytes object with TransMsg.fmt's formatting, returns TypeError
    @staticmethod
    def ungenMsg(data):
        opened = TransMsg.fmt.unpack(data)
        if opened[0] == TransMsg.msgType:
            raw = TransMsg.fmt.unpack(data)
            retVal = TransMsg(*raw[1:])
            retVal.key = cryptostuff.bytesToKey(retVal.key)
            return retVal
        else:
            raise TypeError


# AckMsg -- to acknowledge when a message is recieved
    # always sent via TCP
    # contains 5 things:
        # 1. Message type (MSG_ACK)
        # 2. Node type (whether the sender is a CH or CM as an int)
        # 3. IP of sender
        # 4. Port of sender
        # 5. ACK type (type of message that has been acknowledged -- cannot be MSG_ACK)
class AckMsg:

    fmt = struct.Struct(commonConstants.MSG_ACK_FMT) # the specific format of how we plan on serialising our struct
    
    msgType = commonConstants.MSG_ACK
    def __init__(self, nodeType, ip,port,ackType):
        self.nodeType = nodeType
        self.IP = ip
        self.port = port
        self.ackType = ackType

    # genMsg -- Takes an AckMsg object and seralises it into bytes for sending over a network
    def genMsg(self):
        values = (
            self.msgType,
            self.nodeType,
            bytes(self.IP,'utf-8'),
            self.port,
            self.ackType
        )
        return self.fmt.pack(*values) # splat


    # The below method is static because we want to call it without an instance of AckMsg
    # We can think of it as an alternative constructor (if you're into Java)  
    #  
    # ungenMsg -- takes a serialised AckMsg and returns a AckMsg with all types correctly set
    # If not given a bytes object with AckMsg.fmt's formatting, returns TypeError
    @staticmethod
    def ungenMsg(data):
        opened = AckMsg.fmt.unpack(data)
        if opened[0] == AckMsg.msgType:
            raw = AckMsg.fmt.unpack(data)
            retVal = AckMsg(*raw[1:])
            retVal.IP = retVal.IP.decode('utf-8').replace("\x00",'') # remove null chars at the end of the string
            return retVal
        else:
            raise TypeError






# testing stuff with examples of how to use the packers as well

if __name__ == "__main__":
    import socket
    import cryptostuff
    ip = socket.gethostbyname(socket.gethostname())
    privateKey = cryptostuff.newPrivateKey()
    publicKey = privateKey.public_key()
    message = b"SIGNATURE MESSAGE yoyoyooyoyo jjsjsjsjjs dkdkdkdk nenenen"
    ourSig = cryptostuff.signMsg(privateKey,message)
    test = IntroMsg(commonConstants.TYPE_CM,ip,24232,publicKey)
    print(test.IP,test.port,test.nodeType,test.msgType)
    print(cryptostuff.verifyMsg(publicKey,message,ourSig))

    gen = test.genMsg()
    ungen = IntroMsg.ungenMsg(gen)
    print(ungen.IP,ungen.port,ungen.nodeType,ungen.msgType)
    print(cryptostuff.verifyMsg(ungen.key,message,ourSig))


    test2 = TransMsg(commonConstants.TYPE_CM,ourSig,publicKey)
    gen = test2.genMsg()
    ungen = TransMsg.ungenMsg(gen)
    print(test2.nodeType,test2.signature)
    print(cryptostuff.verifyMsg(test2.key,message,test2.signature))
    print(ungen.nodeType,ungen.signature)
    print(cryptostuff.verifyMsg(ungen.key,message,ungen.signature))

    test3 = AckMsg(commonConstants.TYPE_CM,ip,23423,commonConstants.MSG_INTRO)
    gen = test3.genMsg()
    ungen = AckMsg.ungenMsg(gen)
    print(test3.nodeType,test3.IP,test3.port,test3.ackType)
    print(ungen.nodeType,ungen.IP,ungen.port,ungen.ackType)






    

