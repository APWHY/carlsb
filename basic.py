import CM,CH
import time
from common import handlers

if __name__ == "__main__":
    head = CH.ClusterHead(CH.UDPHandler,CH.TCPHandler)
    mem = CM.ClusterMember(CM.UDPHandler,CM.TCPHandler) 
    print(len(head.CMs))
    head.broadcastIntro()
    print(head.IP,head.BSERVPORT,head.SSERVPORT)
    print(mem.IP,mem.BSERVPORT,mem.SSERVPORT)
    time.sleep(1)
    print(len(head.CMs))
    time.sleep(10)

