import CH
import time, socketserver
from common import consts,utils
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

