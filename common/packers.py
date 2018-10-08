from common import cryptostuff,consts
import struct

# This file contains all the message classes used in the project
# They all implement a simple interface and are used to serialise important information
# That nodes want to send to each other (and unpack them as well)

# Also realised that a way better way to do this would be to use json.dumps
# I mean there are a billion better ways (function array) to do this but oh well
# Will fix this is I have time TODO

# IntroMsg -- for a node to inform another node of its existence
# always sent on the broadcast channel
# contains 5 things:
    # 1. Message type (MSG_INTRO)
    # 2. Node type (whether the sender is a CH or CM as an int)
    # 3. IP address of sender (assumed to be a string)
    # 4. Port number of sender (assumed to be an int)
    # 5. The public key of the sender (assumed to be a cryptography.hazmat.backends.openssl.rsa.RSAPublicKey type)
class IntroMsg:

    fmt = struct.Struct(consts.MSG_INTRO_FMT) # the specific format of how we plan on serialising our struct
    
    msgType = consts.MSG_INTRO
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
        try:
            opened = IntroMsg.fmt.unpack(data)
        except struct.error:
            return None
        if opened[0] == IntroMsg.msgType:
            raw = IntroMsg.fmt.unpack(data)
            retVal = IntroMsg(*raw[1:])
            retVal.IP = retVal.IP.decode('utf-8').replace("\x00",'') # remove null chars at the end of the string
            retVal.key = cryptostuff.bytesToKey(retVal.key)
            return retVal
        else:
            return None



# TransMsg -- for a CM to send a transaction to a CH OR
#             for a CH to tell a CM it has appended the transaction to the blockchain 
    # always sent via TCP
    # contains 4 things:
        # 1. Message type (MSG_TRANS)
        # 2. Node type (whether the sender of the TransMsg is a CH or CM as an int)
        # 3. Signature of the message (the transaction) being sent which we want to append to the blockchain (256 bytes)
        # 4. The public key of the sender of the TransMsg (assumed to be a cryptography.hazmat.backends.openssl.rsa.RSAPublicKey type)
class TransMsg:

    fmt = struct.Struct(consts.MSG_TRANS_FMT) # the specific format of how we plan on serialising our struct
    
    msgType = consts.MSG_TRANS
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
        try:
            opened = TransMsg.fmt.unpack(data)
        except struct.error:
            return None
        if opened[0] == TransMsg.msgType:
            raw = TransMsg.fmt.unpack(data)
            retVal = TransMsg(*raw[1:])
            retVal.key = cryptostuff.bytesToKey(retVal.key)
            return retVal 
        else:
            return None


# AckMsg -- to acknowledge when a message is recieved
    # always sent via TCP
    # contains 6 things:
        # 1. Message type (MSG_ACK)
        # 2. Node type (whether the sender is a CH or CM as an int)
        # 3. IP of sender
        # 4. Port of sender
        # 5. ACK type (type of message that has been acknowledged -- cannot be MSG_ACK)
        # 6. Public Key of the sender
class AckMsg:

    fmt = struct.Struct(consts.MSG_ACK_FMT) # the specific format of how we plan on serialising our struct
    
    msgType = consts.MSG_ACK
    def __init__(self, nodeType, ip,port,ackType,key):
        self.nodeType = nodeType
        self.IP = ip
        self.port = port
        self.ackType = ackType
        self.key = key # this should be a public key

    # genMsg -- Takes an AckMsg object and seralises it into bytes for sending over a network
    def genMsg(self):
        values = (
            self.msgType,
            self.nodeType,
            bytes(self.IP,'utf-8'),
            self.port,
            self.ackType,
            cryptostuff.keyToBytes(self.key)
        )
        return self.fmt.pack(*values) # splat


    # The below method is static because we want to call it without an instance of AckMsg
    # We can think of it as an alternative constructor (if you're into Java)  
    #  
    # ungenMsg -- takes a serialised AckMsg and returns a AckMsg with all types correctly set
    # If not given a bytes object with AckMsg.fmt's formatting, returns TypeError
    @staticmethod
    def ungenMsg(data):
        try:
            opened = AckMsg.fmt.unpack(data)
        except struct.error:
            return None
        if opened[0] == AckMsg.msgType:
            raw = AckMsg.fmt.unpack(data)
            retVal = AckMsg(*raw[1:])
            retVal.IP = retVal.IP.decode('utf-8').replace("\x00",'') # remove null chars at the end of the string
            retVal.key = cryptostuff.bytesToKey(retVal.key)
            return retVal
        else:
            return None



# VerifyMsg -- for a CM to ask a CH to verify a message OR
#             for a CH to tell a CM the result of a verification process 
    # always sent via TCP
    # contains 4 things:
        # 1. Message type (MSG_VERIFY)
        # 2. Node type (whether the sender of the VerifyMsg is a CH or CM as an int)
        # 3. Signature of the message (the transaction) which we want to verify (256 bytes)
        # 4. The public key of the sender of the transaction that we want to verify (assumed to be a cryptography.hazmat.backends.openssl.rsa.RSAPublicKey type)
        # 5. The public key of the sender of the VerifyMsg (assumed to be a cryptography.hazmat.backends.openssl.rsa.RSAPublicKey type)
        # 6. The result of the verification process as a bool (ignored when sent by a CM)
class VerifyMsg:

    fmt = struct.Struct(consts.MSG_VERIFY_FMT) # the specific format of how we plan on serialising our struct
     
    msgType = consts.MSG_VERIFY
    def __init__(self, nodeType, signature,keyTransSender,keySender, result):
        self.nodeType = nodeType
        self.signature = signature
        self.keyTransSender = keyTransSender # this should be a public key
        self.keySender = keySender
        self.result = result


    # genMsg -- Takes a VerifyMsg object and seralises it into bytes for sending over a network
    def genMsg(self):
        values = (
            self.msgType,
            self.nodeType,
            self.signature,
            cryptostuff.keyToBytes(self.keyTransSender),
            cryptostuff.keyToBytes(self.keySender),
            self.result
        )
        return self.fmt.pack(*values) # splat


    # The below method is static because we want to call it without an instance of VerifyMsg
    # We can think of it as an alternative constructor (if you're into Java)  
    #  
    # ungenMsg -- takes a serialised VerifyMsg and returns a VerifyMsg with all types correctly set
    # If not given a bytes object with VerifyMsg.fmt's formatting, returns TypeError
    @staticmethod
    def ungenMsg(data):
        try:
            opened = VerifyMsg.fmt.unpack(data)
        except struct.error:
            return None

        if opened[0] == VerifyMsg.msgType:
            raw = VerifyMsg.fmt.unpack(data)
            retVal = VerifyMsg(*raw[1:])
            retVal.keyTransSender = cryptostuff.bytesToKey(retVal.keyTransSender)
            retVal.keySender = cryptostuff.bytesToKey(retVal.keySender)
            return retVal 
        else:
            return None


# KUIMsg -- for a CM to notify a CH of a change in it's public key
    # always sent via TCP
    # contains 4 things:
        # 1. Message type (MSG_KUI)
        # 2. Node type (whether the sender of the KUIMsg is a CH or CM as an int)
        # 3. The old public key of the sender of the KUIMsg (assumed to be a cryptography.hazmat.backends.openssl.rsa.RSAPublicKey type)
        # 4. The new public key of the sender of the KUIMsg (assumed to be a cryptography.hazmat.backends.openssl.rsa.RSAPublicKey type)
class KUIMsg:

    fmt = struct.Struct(consts.MSG_KUI_FMT) # the specific format of how we plan on serialising our struct
    
    msgType = consts.MSG_KUI
    def __init__(self, nodeType, signature,keyOld, keyNew):
        self.nodeType = nodeType
        self.signature = signature
        self.keyOld = keyOld # this should be a public key
        self.keyNew = keyNew

    # genMsg -- Takes a KUIMsg object and seralises it into bytes for sending over a network
    def genMsg(self):
        values = (
            self.msgType,
            self.nodeType,
            self.signature,
            cryptostuff.keyToBytes(self.keyOld),
            cryptostuff.keyToBytes(self.keyNew)
        )
        return self.fmt.pack(*values) # splat


    # The below method is static because we want to call it without an instance of KUIMsg
    # We can think of it as an alternative constructor (if you're into Java)  
    #  
    # ungenMsg -- takes a serialised KUIMsg and returns a KUIMsg with all types correctly set
    # If not given a bytes object with KUIMsg.fmt's formatting, returns TypeError
    @staticmethod
    def ungenMsg(data):
        try:
            opened = KUIMsg.fmt.unpack(data)
        except struct.error:
            return None
        if opened[0] == KUIMsg.msgType:
            raw = KUIMsg.fmt.unpack(data)
            retVal = KUIMsg(*raw[1:])
            retVal.keyOld = cryptostuff.bytesToKey(retVal.keyOld)
            retVal.keyNew = cryptostuff.bytesToKey(retVal.keyNew)
            return retVal 
        else:
            return None

    



# MsgMsg -- not needed for this network but instead used as a helper msg for demonstration and testing purposes
#           used to tell all nodes where a message can be downloaded from and what it's signature is
#           for general use this function should be implemented outside of the network but it's easier to have it in here for now
    # always sent via UDP
    # contains 4 things:
        # 1. Message type (MSG_MSG)
        # 2. Node type (whether the sender of the MsgMsg is a CH or CM as an int)
        # 3. IP address where the message can be downloaded
        # 4. Port where the message can be downloaded
        # 5. Signature of the message sent
        # 6. Public Key of the sender
class MsgMsg:

    fmt = struct.Struct(consts.MSG_MSG_FMT) # the specific format of how we plan on serialising our struct
    
    msgType = consts.MSG_MSG
    def __init__(self, nodeType, ip, port, signature,key):
        self.nodeType = nodeType
        self.IP = ip
        self.port = port
        self.signature = signature
        self.key = key # this should be a public key


    # genMsg -- Takes a MsgMsg object and seralises it into bytes for sending over a network
    def genMsg(self):
        values = (
            self.msgType,
            self.nodeType,
            bytes(self.IP,'utf-8'),
            self.port,
            self.signature,
            cryptostuff.keyToBytes(self.key),
        )
        return self.fmt.pack(*values) # splat


    # The below method is static because we want to call it without an instance of MsgMsg
    # We can think of it as an alternative constructor (if you're into Java)  
    #  
    # ungenMsg -- takes a serialised MsgMsg and returns a MsgMsg with all types correctly set
    # If not given a bytes object with MsgMsg.fmt's formatting, returns TypeError
    @staticmethod
    def ungenMsg(data):
        try:
            opened = MsgMsg.fmt.unpack(data)
        except struct.error:
            return None
        if opened[0] == MsgMsg.msgType:
            raw = MsgMsg.fmt.unpack(data)
            retVal = MsgMsg(*raw[1:])
            retVal.IP = retVal.IP.decode('utf-8').replace("\x00",'') # remove null chars at the end of the string
            retVal.key = cryptostuff.bytesToKey(retVal.key)
            return retVal 
        else:
            return None

    


