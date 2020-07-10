from multiprocessing import Pool
from functools import partial

from multiprocessing import Process
from multiprocessing.pool import Pool

class NoDaemonProcess(Process):
    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

class MyPool(Pool):
    Process = NoDaemonProcess

def mass_transfer(index, from_member, to_member):

    while True:
        try:
            downloader, packet = from_member.create_giver(index)
            uploader = to_member.create_receiver(packet)

            done = False
            while done is False:
                status,done = downloader.next_chunk()
                uploader.write(downloader.getvalue())
            uploader.close()
            break
        except Exception as e:
            pass

class Shelter():

    def __init__(self, workers):

        self.members = {}
        self.workers = workers

    def register(self, name, object):

        self.members[name] = object

    def transfer(self,_from,_to):

        from_member = self.members[_from].make_member()
        to_member = self.members[_to].make_member()

        print("Transfering {} items".format(len(from_member)))
        
        target = partial(mass_transfer, from_member=from_member, to_member=to_member) 
        p = Pool(self.workers)
        p.map(target, range(len(from_member)))
        p.close()
        p.join()

        print("Transfer done")
