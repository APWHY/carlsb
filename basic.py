# Run this if you want to see that a simple network can be set up and left idle
# Just tries to make a CH and a CM and have them connect to each other
import CM,CH
import time
from common import handlers

if __name__ == "__main__":
    head = CH.ClusterHead(CH.UDPHandler,CH.TCPHandler,spoofContract=True)
    mem = CM.ClusterMember(CM.UDPHandler,CM.TCPHandler) 
    print(len(head.CMs))
    head.broadcastIntro()
    print(head.IP,head.BSERVPORT,head.SSERVPORT)
    print(mem.IP,mem.BSERVPORT,mem.SSERVPORT)
    time.sleep(1)
    print(len(head.CMs))
    time.sleep(10)

