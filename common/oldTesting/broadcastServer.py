import socket


# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind(('', 12345))
# print("setup done, listening")
# sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock2.bind(("192.168.0.14",13456))
# sock2.sendto('AAAAAAAAAAAAAAAAAAAAAAAA'.encode("utf8"),('192.168.0.254',9999))
# while True:
#      try:
#          addr, data = sock.recvfrom(4096)
#          print("found stuff")
#          print(addr, data)
#      except Exception as e:
#          print("Got exception trying to recv %s" % e)
#          raise StopIteration



# # # server.py
import socket
def do_some_stuffs_with_input(input_string):  
    """
    This is where all the processing happens.

    Let's just read the string backwards
    """

    print("Processing the input ...")
    return input_string[::-1]

def client_thread(data, ip, port, MAX_BUFFER_SIZE = 4096):

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

    res = do_some_stuffs_with_input(input_from_client)
    print("Result of processing {} is: {}".format(input_from_client, res))

    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
    soc.sendto(res.encode("utf8"),(ip, int(port))) # we must encode the string to bytes  

    print('Connection ' + ip + ':' + port + " ended")

def start_server():


    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # this is for easy starting/killing the app
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Broadcast Socket created')

    try:
        ip = '0.0.0.0'
        # ip = "192.168.43.177"
        # ip = "192.168.0.14"
        # ip = "127.0.0.1"
        soc.bind((ip, 28196)) # match this with BROADCAST_PORT in common.consts
        print('Socket bind complete')
    except socket.error as msg:
        import sys
        print('Bind failed. Error : ' + str(sys.exc_info()) + " msg: " + str(msg))
        sys.exit()

    print(soc.getsockname())


    #Start listening on socket
    # soc.listen(10)

    # print('Socket now listening')

    # for handling task in separate jobs we need threading
    from threading import Thread

    # this will make an infinite loop needed for 
    # not reseting server for every client
    while True:
        # conn, addr = soc.accept()
        # ip, port = str(addr[0]), str(addr[1])
        # print('Accepting connection from ' + ip + ':' + port)
        data , addr = soc.recvfrom(4096)
        ip, port = str(addr[0]), str(addr[1])
        print('Received %s from %s', data, addr)
        try:
            Thread(target=client_thread, args=(data, ip, port)).start()
        except:
            print("Terible error!")
            import traceback
            traceback.print_exc()
    soc.close()

start_server()  