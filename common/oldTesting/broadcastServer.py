# simple server for receiving udp packets
# only purpose is to test functionality manually
# large chunk copied off some online tutorial
import socket

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
        soc.bind((ip, 28196)) # match this with BROADCAST_PORT in common.consts
        print('Socket bind complete')
    except socket.error as msg:
        import sys
        print('Bind failed. Error : ' + str(sys.exc_info()) + " msg: " + str(msg))
        sys.exit()

    print(soc.getsockname())

    from threading import Thread

    # this will make an infinite loop needed for 
    # not reseting server for every client
    while True:
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