# code for a node 'peer' object
# intended to be the main point of contact for all communications

import socket
import socketserver
from threading import Thread
import select
from common import consts,utils
import time





# The commonNode class is intended to be the interface behind which all socket/socketserver-level
# communications are done through. It groups the sending of TCP and UDP packets with the
# servers responsible for recieving them
class commonNode():
	BSERVPORT = consts.BROADCAST_PORT 
						
	def __init__(self, broadcastHandler, streamHandler):
		# we get our own ip
		self.IP = utils.get_ip()
		# set up our streaming server
		self.streamServer = socketserver.TCPServer((self.IP,0), streamHandler )
		# now we can get the port our streaming server is bound to
		self.SSERVPORT = self.streamServer.socket.getsockname()[1]

		# finally, we set up the broadcast server
		# allow multiple processes to listen on the same port since we want this to be the case
		# for broadcasts
		socketserver.UDPServer.allow_reuse_address = True
		self.broadcastServer = socketserver.UDPServer((self.IP,self.BSERVPORT), broadcastHandler)
		tempSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		tempSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		tempSocket.bind(('0.0.0.0',self.BSERVPORT))
		# We manually remake the socket so that it can handle broadcasts instead of normal udp packets
		self.broadcastServer.socket = tempSocket

	

	def sendTCP(self, msg, ip, port):

		soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
		soc.connect((ip,port))
		soc.send(msg) # we must encode the string to bytes  
	def broadcast(self,msg):
		# we do not expect to receive a result from a broadcast
		# when a node receives a broadcast (which should contain an address to reply to)
		# the reply is made to that address, not on the broadcast address


		soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
		soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
		soc.bind((self.IP,0))
		soc.sendto(msg, (('<broadcast>',consts.BROADCAST_PORT)))
 



	def hold(self): # makes all servers serveforever until keyboardInterrupt
					# each thread will block until __main__ finishes execution
		Thread(target=self.streamServer.serve_forever, daemon=True).start() 
		Thread(target=self.broadcastServer.serve_forever, daemon=True).start() 

