
from multiprocessing import Process
from multiprocessing.pool import Pool

class NoDaemonProcess(Process):
    # make 'daemon' attribute always return False

    # def __init__(self, **kwargs):
    #     super(Processor, self).__init__()
    #     self.group = None

    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)


class MyPool(Pool):

    def Process(self, *args, **kwds):
        proc = super(MyPool, self).Process(*args, **kwds)
        proc.__class__ = NoDaemonProcess

        return proc