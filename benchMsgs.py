# Benchmark to see how many messages (at max throughput) a CH can handle before it breaks
# Run with demoCH or spoofCH
import CM
import time, sys,timeit , _thread
from common import consts,utils,cryptostuff,packers



class benchMsgs(CM.ClusterMember):
    count = 0
    # this can be literally anything so yeah
    default_msg = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est 
                laborum.'''.encode('utf-8')
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs) #do standard CH stuff
        self.httpIP = utils.get_ip()
        self.lock = _thread.allocate_lock() # to stop sendMsg from clashing with itself
        print("benchMsgs serving")

    def sendMsg(self):
        self.lock.acquire()
        self.msgSig = cryptostuff.signMsg(self.privateKey,self.default_msg)
        self.sendTransaction(self.inc,self.msgSig)

    def inc(self):
        self.count += 1
        self.lock.release()
        
def test(spammer, max):
    spammer.count = 0
    spammer.max = max

    while spammer.count != spammer.max:
         spammer.sendMsg()


if __name__ == "__main__":

    spammer = benchMsgs(CM.UDPHandler,CM.TCPHandler)
    print(spammer.BSERVPORT,spammer.SSERVPORT,spammer.IP)
    print("waiting for OEM to acquire CH")
    while not spammer.CH.exists: # lazy way of doing things but it works for now
        time.sleep(1)
        print('.')
    # change parameters of the next line depending on what you want to test
    t = timeit.repeat("test(spammer,max)", setup="from __main__ import test", globals={"max":1, "spammer":spammer}, number=1,repeat=10)
    print(t)
    print(sum(t)/float(len(t)))
