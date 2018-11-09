# old (very broken) implementation of the commonNode class
import socket
from threading import Thread
import select

class commonNode():
	BSERVPORT = 12345
	def __init__(self, port, bClientHandle, bServerHandle, sClientHandle, sServerHandle):
		# set up socket to send broadcasts
		self.BSERVPORT = port
		self.bClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
		self.bClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

		self.sClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
		ip = '0.0.0.0'
		# ip = "192.168.0.14"
		# ip = "127.0.0.1"
		try:
			Thread(target=self.start_stream_server, args=(ip,self.BSERVPORT,sServerHandle)).start()
		except:
			print("Couldn't start stream server!")
			import traceback
			traceback.print_exc()


		try:
			Thread(target=self.start_broadcast_server, args=(ip,self.BSERVPORT,bServerHandle)).start()
		except:
			print("Couldn't start broadcast server!")
			import traceback
			traceback.print_exc()

	def broadcast(self,inputStr,addr,port):
		self.bClientSocket.sendto(inputStr.encode("utf-8"), ((addr,port)))
		# we do not wait for a response broadcast packets should provide a return ip/port combination for clients attempt connection on
		return


	def send(self,data, addr, port):
		self.sClientSocket.connect((addr, port))
		self.sClientSocket.send(data.encode("utf8")) # we must encode the string to bytes  
		result_bytes = self.sClientSocket.recv(4096) # the number means how the response can be in bytes  
		result_string = result_bytes.decode("utf8") # the return will be in bytes, so decode
		return result_string	

	def start_broadcast_server(self, addr, port, handlefunc):
		self.bServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# this is for easy starting/killing the app
		self.bServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print('Broadcast Socket created')

		try:
			
			self.bServerSocket.bind((addr, port))
			print('Broadcst socket bind complete')
		except socket.error as msg:
			import sys
			print('Bind failed. Error : ' + str(sys.exc_info()) + " msg: " + msg)
			sys.exit()

		print('Broadcst socket now listening')


		# this will make an infinite loop needed for 
		# not reseting server for every client
		while True:

			r, _, _ = select.select([self.bServerSocket],[],[])
			if r:
				data , addr = self.bServerSocket.recvfrom(4096)
				ip, port = str(addr[0]), str(addr[1])
				print('Received %s from %s', data, addr)
				try:
					Thread(target=self.broadcast_client_thread, args=(data, ip, port, handlefunc)).start()
				except:
					print("Could not start reply broadcast client thread!")
					import traceback
					traceback.print_exc()
		self.bServerSocket.close()

	# higher class function that will take the input and pass it into another function of the programmer's choosing
	def broadcast_client_thread(self,data, ip, port, handlefunc, MAX_BUFFER_SIZE = 4096):

		# the input is in bytes, so decode it
		# input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)

		# MAX_BUFFER_SIZE is how big the message can be
		# this is test if it's sufficiently big
		input_from_client_bytes = data
		import sys
		siz = sys.getsizeof(input_from_client_bytes)
		if  siz >= MAX_BUFFER_SIZE:
			print("The length of input is probably too long: {}".format(siz))

		# decode input and strip the end of line
		input_from_client = input_from_client_bytes.decode("utf8").rstrip()

		res = handlefunc(input_from_client)
		print("Result of processing {} is: {}".format(input_from_client, res))

		soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
		soc.sendto(res.encode("utf8"),(ip, int(port))) # we must encode the string to bytes  

		print('Connection ' + ip + ':' + port + " ended")
	
	def start_stream_server(self,addr,port, handlefunc):
		self.sServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# this is for easy starting/killing the app
		self.sServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print('Stream Socket created')

		try:
			# ip = '0.0.0.0'
			# ip = "192.168.0.14"
			# ip = "127.0.0.1"
			self.sServerSocket.bind((addr,port))
			print('Stream socket bind complete')
		except socket.error as msg:
			import sys
			print('Bind failed. Error : ' + str(sys.exc_info()) + 'msg: ' + msg)
			sys.exit()

		#Start listening on socket
		self.sServerSocket.listen(10)
		print('Stream socket now listening')


		# this will make an infinite loop needed for 
		# not reseting server for every client
		while True:
			r, _, _ = select.select([self.bServerSocket],[],[])
			if r:
				conn, addr = self.sServerSocket.accept()
				ip, port = str(addr[0]), str(addr[1])
				print('Accepting connection from ' + ip + ':' + port)
				try:
					Thread(target=self.stream_client_thread, args=(conn, ip, port, handlefunc)).start()
				except:
					print("Terible error!")
					import traceback
					traceback.print_exc()
		self.sServerSocket.close()


	def stream_client_thread(self,conn, ip, port,handlefunc, MAX_BUFFER_SIZE = 4096):

		# the input is in bytes, so decode it
		input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)

		# MAX_BUFFER_SIZE is how big the message can be
		# this is test if it's sufficiently big
		import sys
		siz = sys.getsizeof(input_from_client_bytes)
		if  siz >= MAX_BUFFER_SIZE:
			print("The length of input is probably too long: {}".format(siz))

		# decode input and strip the end of line
		input_from_client = input_from_client_bytes.decode("utf8").rstrip()

		res = handlefunc(input_from_client)
		print("Result of processing {} is: {}".format(input_from_client, res))

		vysl = res.encode("utf8")  # encode the result string
		conn.sendall(vysl)  # send it to client
		conn.close()  # close connection
		print('Connection ' + ip + ':' + port + " ended")


	def shutdown(self):
		self.bClientSocket.shutdown(socket.SHUT_RDWR)
		self.sClientSocket.shutdown(socket.SHUT_RDWR)
		self.bServerSocket.shutdown(socket.SHUT_RDWR)
		self.sServerSocket.shutdown(socket.SHUT_RDWR)