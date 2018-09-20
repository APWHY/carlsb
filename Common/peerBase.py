# code for a node 'peer' object
# intended to be the main point of contact for all communications
# packet stuff may or may not be done outside of this -- haven't decided if this is going to just handle socket communications
# or whether or not it will do the signature stuff as well
# I think that is unlikely

import socket
import socketserver
from threading import Thread
import select
from common import consts
import time






class commonNode():
	BSERVPORT = consts.BROADCAST_PORT 
						
	def __init__(self, broadcastHandler, streamHandler):
		# we get our own ip
		self.IP = socket.gethostbyname(socket.gethostname())
		print(broadcastHandler,streamHandler)
		# set up our streaming server
		self.streamServer = socketserver.TCPServer((self.IP,0), streamHandler )
		# now we can get the port our streaming server is bound to
		self.SSERVPORT = self.streamServer.socket.getsockname()[1]

		# finally, we set up the broadcast server
		# allow multiple processes to listen on the same port since we want this to be the case
		# for broadcasts
		socketserver.UDPServer.allow_reuse_address = True
		self.broadcastServer = socketserver.UDPServer((self.IP,self.BSERVPORT), broadcastHandler)

	

	def sendTCP(self, msg, ip, port):

		soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
		soc.connect((ip,port))
		soc.send(msg) # we must encode the string to bytes  
	def broadcast(self,msg):
		# we do not expect to receive a result from a broadcast
		# when a node receives a broadcast (which should contain an address to reply to)
		# the reply is made to that address, not on the broadcast address

		print(str(len(msg)) + "is message length")

		soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
		soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
		soc.sendto(msg, (('<broadcast>',consts.BROADCAST_PORT)))
 



	def hold(self): # makes all servers serveforever until keyboardInterrupt
					# each thread will block until __main__ finishes execution
		Thread(target=self.streamServer.serve_forever, daemon=True).start() 
		Thread(target=self.broadcastServer.serve_forever, daemon=True).start() 

