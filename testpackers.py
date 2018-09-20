import socket
from common import cryptostuff, packers, consts

# testing stuff with examples of how to use the packers as well
# messy having all tests out here but I can't be boethered to fix python's crazy import rules

if __name__ == "__main__":

    ip = socket.gethostbyname(socket.gethostname())
    privateKey = cryptostuff.newPrivateKey()
    publicKey = privateKey.public_key()
    message = b"SIGNATURE MESSAGE yoyoyooyoyo jjsjsjsjjs dkdkdkdk nenenen"
    ourSig = cryptostuff.signMsg(privateKey,message)
    test = packers.IntroMsg(consts.TYPE_CM,ip,24232,publicKey)
    print(test.IP,test.port,test.nodeType,test.msgType)
    print(cryptostuff.verifyMsg(publicKey,message,ourSig))

    gen = test.genMsg()
    ungen = packers.IntroMsg.ungenMsg(gen)
    print(ungen.IP,ungen.port,ungen.nodeType,ungen.msgType)
    print(cryptostuff.verifyMsg(ungen.key,message,ourSig))


    test2 = packers.TransMsg(consts.TYPE_CM,ourSig,publicKey)
    gen = test2.genMsg()
    ungen = packers.TransMsg.ungenMsg(gen)
    print(test2.nodeType,test2.signature)
    print(cryptostuff.verifyMsg(test2.key,message,test2.signature))
    print(ungen.nodeType,ungen.signature)
    print(cryptostuff.verifyMsg(ungen.key,message,ungen.signature))

    test3 = packers.AckMsg(consts.TYPE_CM,ip,23423,consts.MSG_INTRO,publicKey)
    gen = test3.genMsg()
    ungen = packers.AckMsg.ungenMsg(gen)
    print(test3.nodeType,test3.IP,test3.port,test3.ackType)
    print(ungen.nodeType,ungen.IP,ungen.port,ungen.ackType)


