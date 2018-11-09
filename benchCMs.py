# Benchmark testing the number of CMs a single CH can handle concurrently
# Run with demoCH or spoofCH
import CM
import time, sys,timeit , _thread
from threading import Thread
from common import consts,utils,cryptostuff,packers
from functools import partial


class benchCMs(CM.ClusterMember):
    count = 0
    # this can be literally anything so yeah
    default_msg = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est 
                laborum.'''.encode('utf-8')
    def __init__(self, id, *args, **kwargs):
        super().__init__(*args,**kwargs) #do standard CH stuff
        self.id = id
        self.httpIP = utils.get_ip()
        self.lock = _thread.allocate_lock() # to stop sendMsg from clashing with itself


    def sendMsg(self, handler):
        self.lock.acquire()
        self.msgSig = cryptostuff.signMsg(self.privateKey,self.default_msg)
        self.sendTransaction(partial(handler,self.id),self.msgSig)

class Counter():
    count = []
    def __init__(self,start,max):
        self.start = start
        self.max = max
    def inc(self,i):
        self.count.append(i)
        if len(self.count) == self.max:
            timeEnd = time.clock()
            self.timeStop(timeEnd)

    def timeStop(self,stop):
        print(stop-self.start)



def test(spammers, max):

    count = Counter(time.clock(), max)
    print(len(spammers))
    for s in spammers:
        Thread(target=s.sendMsg, daemon=True, args=(count.inc,)).start()

    time.sleep(500)



if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python N")
        print("Where N is number of messages to send")
        sys.exit(0)
    print("max is {}", sys.argv[1])
    spammers = []
    print("booting spammers")
    start = time.clock()
    for i in range(1,10):
        spammers.append(benchCMs(i,CM.UDPHandler,CM.TCPHandler))



    for s in spammers:
        while not s.CH.exists:
            time.sleep(1)
    end = time.clock()
    time.sleep(1)
    print("acquire spammers time:", end-start)
    test(spammers,len(spammers))



