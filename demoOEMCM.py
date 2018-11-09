# part of the demo. Run with demoCH and multiple instances of demoCarCM
import CM
import time, socketserver, os
from common import consts,utils,cryptostuff,packers
from simplehttp import simpleServer
from threading import Thread

# The role of the OEM in the demo is to prepare a message and send it to the CH before serving it
# It then tells the car(s) to download the message
class demoOEM(CM.ClusterMember):

    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs) #do standard CH stuff
        self.httpIP = utils.get_ip()
        self.fileServer = socketserver.TCPServer((self.httpIP,consts.HTTP_PORT),simpleServer.SimpleFileHandler)
        print("demoOEM serving")

    def prepareServer(self):
        testFilePath =  os.path.join(os.path.curdir, 'simplehttp', 'download','example')
        self.fileServer.serving = testFilePath
        f = open(testFilePath,"rb")
        msg = f.read()
        self.msgSig = cryptostuff.signMsg(self.privateKey,msg)
        self.sendTransaction(self.serveFile,self.msgSig)
        print("message signed, sending transaction...")

    def serveFile(self):
        print("transaction posted, serving file!")
        Thread(target=self.fileServer.serve_forever,daemon=True).start()
        # slight probability for race condition here but it'll be fine for a demo
        msg = packers.MsgMsg(consts.TYPE_CM,self.httpIP,consts.HTTP_PORT,self.msgSig,self.pubKey).genMsg()
        self.broadcast(msg)




if __name__ == "__main__":
    oem = demoOEM(CM.UDPHandler,CM.TCPHandler)
    print("waiting for OEM to acquire CH")
    while not oem.CH.exists: # lazy way of doing things but it works for now
        time.sleep(1)
        print('.')
    oem.prepareServer()
    time.sleep(300)
