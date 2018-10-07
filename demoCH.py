import CH
import time, socketserver
from common import handlers,consts,utils
from simplehttp import simpleServer
from threading import Thread


class demoCH(CH.ClusterHead):

	def __init__(self,*args, **kwargs):
		super().__init__(*args,**kwargs) #do standard CH stuff
		print("demoCH serving")
		super().broadcastIntro()





if __name__ == "__main__":
	head = demoCH(CH.UDPHandler,CH.TCPHandler)
	time.sleep(300)

    # head = CH.ClusterHead(CH.UDPHandler,CH.TCPHandler)
    # mem = CM.ClusterMember(CM.UDPHandler,CM.TCPHandler) 
    # print(len(head.CMs))
    # head.broadcastIntro()
    # print(head.IP,head.BSERVPORT,head.SSERVPORT)
    # print(mem.IP,mem.BSERVPORT,mem.SSERVPORT)
    # time.sleep(1)
    # print(len(head.CMs))
    # time.sleep(10)

