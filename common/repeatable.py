import threading,time

# simple module to repeat any job every <delay> seconds
# The scheduling library does this really well but is pretty overkill -- if you need 
# more functionality in the future consider swapping over to it 
# but this is honestly enough for most of the things that are required


class job():
    def __init__(self, target, delay):
        self.target = target
        self.delay = delay
        self.running = False

    # start the repeatable job
    def start(self):
        self.running = True
        self.repeater = threading.Thread(target=self.rerun, daemon=True).start()

    # responsible for the actual act of repeating -- should never be explicitly called
    def rerun(self):
        while self.running:
            self.target()
            time.sleep(self.delay)

    # idk why you'd ever want to pause a job but there you have it
    def pause(self):
        self.running = False #boolean assignment is atomic so we don't have anything to worry aobut


