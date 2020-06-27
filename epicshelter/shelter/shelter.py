

class Shelter():

    def __init__(self):

        self.members = {}

    def register(self, name, object):

        self.members[name] = object

    def transfer(self,_from,_to):

        from_member = self.members[_from].make_member()
        to_member = self.members[_to].make_member()

        print("Transfering {} items".format(len(from_member)))

        for i in range(len(from_member)):
            downloader, packet = from_member.create_giver(i)
            uploader = to_member.create_receiver(packet)

            done = False
            while done is False:
                status,done = downloader.next_chunk()
                uploader.write(downloader.getvalue())
            uploader.close()