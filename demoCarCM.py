import CM
import time, urllib.request
from common import handlers, cryptostuff,utils


class Car(CM.ClusterMember):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def checkChain(self, ip, port, signature, pubKey):
        print("---------------------------------------------------------------------")
        self.msgIP = ip
        self.msgPort = port
        self.msgSig = signature
        self.msgPubKey = pubKey
        super().verifyTransaction(self.retrieve, pubKey, signature)


    def retrieve(self, result):
        if result:
            addr = "http://" + self.msgIP +  ":" + str(self.msgPort)
            msgf = urllib.request.urlopen(addr)
            msg = msgf.read()
            print(msg)
            if cryptostuff.verifyMsg(self.pubKey,msg,self.msgSig):
                print("message is verified properly!")
                return True
            else:
                print("something went wrong with checking the message....n")
                return False
        else:
            print("signature not verified on chain")
            return False



if __name__ == "__main__":
    print("IP is: " + utils.get_ip())
    test = Car(CM.UDPHandler,CM.TCPHandler)
    test.addDownloadFunc(test.checkChain)
    time.sleep(300)



OEM_IP = "0.0.0.0"