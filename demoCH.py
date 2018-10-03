import CH
import time, socketserver
from common import handlers,consts,utils
from simplehttp import simpleServer
from threading import Thread


class demoCH(CH.ClusterHead):

	def __init__(self,*args, **kwargs):
		super().__init__(*args,**kwargs) #do standard CH stuff
		self.httpIP = utils.get_ip()
		self.fileServer = socketserver.TCPServer((self.httpIP,consts.HTTP_PORT),simpleServer.SimpleFileHandler)
		print("demoCH serving")
		super().broadcastIntro()

	def serveFile(self):
		Thread(target=self.fileServer.serve_forever,daemon=True).start()




if __name__ == "__main__":
	head = demoCH(CH.UDPHandler,CH.TCPHandler)
	time.sleep(10)

    # head = CH.ClusterHead(CH.UDPHandler,CH.TCPHandler)
    # mem = CM.ClusterMember(CM.UDPHandler,CM.TCPHandler) 
    # print(len(head.CMs))
    # head.broadcastIntro()
    # print(head.IP,head.BSERVPORT,head.SSERVPORT)
    # print(mem.IP,mem.BSERVPORT,mem.SSERVPORT)
    # time.sleep(1)
    # print(len(head.CMs))
    # time.sleep(10)

