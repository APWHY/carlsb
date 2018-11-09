# The counterpart to demoCH. Does exactly the same thing but without the need for a ledger
import CH
import time, socketserver
from common import consts,utils
from simplehttp import simpleServer
from threading import Thread

# This can eventually be joined with demoCH by having the program accept spoofContract as an argument
class SpoofCH(CH.ClusterHead):

	def __init__(self,*args, **kwargs):
		super().__init__(*args,**kwargs,spoofContract=True) #do standard CH stuff
		print("SpoofCH serving")
		super().broadcastIntro()




if __name__ == "__main__":
	head = SpoofCH(CH.UDPHandler,CH.TCPHandler)
	print(head.BSERVPORT,head.SSERVPORT,head.IP)
	time.sleep(3000)

