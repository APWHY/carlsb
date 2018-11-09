import CM
import time, socketserver, os
from common import consts,utils,cryptostuff,packers
from simplehttp import simpleServer
from threading import Thread


class testKUI(CM.ClusterMember):

    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs) #do standard CH stuff
        print("testKUI serving")





if __name__ == "__main__":
    oem = testKUI(CM.UDPHandler,CM.TCPHandler, hasKUI=False)
    print("waiting for OEM to acquire CH")
    while not oem.CH.exists: # lazy way of doing things but it works for now
        time.sleep(1)
        print('.')
    time.sleep(300)
