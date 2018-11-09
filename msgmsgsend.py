# super basic ping sender
# Used to check broadcasts are working properly on CHs and CMs
import CM
import time, urllib.request
from common import handlers, cryptostuff


class Car(CM.ClusterMember):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)



if __name__ == "__main__":
    test = Car(CM.UDPHandler,CM.TCPHandler)
    while True:
        time.sleep(1)
        test.broadcast(b"bing")


