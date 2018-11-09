import CH
import time, socketserver
from common import consts,utils
from simplehttp import simpleServer
from threading import Thread


class SpoofCH(CH.ClusterHead):

	def __init__(self,*args, **kwargs):
		super().__init__(*args,**kwargs,spoofContract=True) #do standard CH stuff
		print("SpoofCH serving")
		super().broadcastIntro()




if __name__ == "__main__":
	head = SpoofCH(CH.UDPHandler,CH.TCPHandler)
	print(head.BSERVPORT,head.SSERVPORT,head.IP)
	time.sleep(3000)

