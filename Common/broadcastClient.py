# client.py

import socket
# from socket import SOL_SOCKET, SO_TYPE
# ip = '192.168.0.255'
# ip = "192.168.0.14"
# ip = "127.0.0.1"

soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
# soc.bind((ip,12346))
# soc.connect((ip, 12345))

clients_input = input("What you want to broadcast, my dear client?\n")  

# soc.send(clients_input.encode("utf8")) # we must encode the string to bytes  
soc.sendto(clients_input.encode("utf8"), (('192.168.0.255',12345)))

result_bytes, blah = soc.recvfrom(4096) # the number means how the response can be in bytes  
result_string = result_bytes.decode("utf8") # the return will be in bytes, so decode

print("Result from server is {}".format(result_string))  



    # soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # # this is for easy starting/killing the app
    # soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # print('Broadcast Socket created')

    # try:
    #     ip = '0.0.0.0'
    #     # ip = "192.168.0.14"
    #     # ip = "127.0.0.1"
    #     soc.bind((ip, 12345))
    #     print('Socket bind complete')
    # except socket.error as msg:
    #     import sys
    #     print('Bind failed. Error : ' + str(sys.exc_info()))
    #     sys.exit()

    # #Start listening on socket
    # # soc.listen(10)

    # # print('Socket now listening')

    # # for handling task in separate jobs we need threading
    # from threading import Thread

    # # this will make an infinite loop needed for 
    # # not reseting server for every client
    # while True:
    #     # conn, addr = soc.accept()
    #     # ip, port = str(addr[0]), str(addr[1])
    #     # print('Accepting connection from ' + ip + ':' + port)
    #     data , addr = soc.recvfrom(4096)
    #     ip, port = str(addr[0]), str(addr[1])
    #     print('Received %s from %s', data, addr)
    #     try:
    #         Thread(target=client_thread, args=(data, ip, port)).start()
    #     except:
    #         print("Terible error!")
    #         import traceback
    #         traceback.print_exc()
    # soc.close()