# Can be part of the demo but stands on its own as well
import CH
import time, socketserver
from common import consts,utils
from simplehttp import simpleServer
from threading import Thread

# demoCH is a class that starts up an instance of a CH that is ready to perform its role
# It works fine for almost all applications unless you want to spoof the chain
# whereupon you would want to use spoofCH instead.
class DemoCH(CH.ClusterHead):

	def __init__(self,*args, **kwargs):
		super().__init__(*args,**kwargs) #do standard CH stuff
		print("DemoCH serving")
		super().broadcastIntro()





if __name__ == "__main__":
	head = DemoCH(CH.UDPHandler,CH.TCPHandler)
	time.sleep(300)

