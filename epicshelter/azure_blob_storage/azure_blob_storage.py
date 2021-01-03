import os 
from azure.storage.blob import BlobServiceClient, ContainerClient
from smart_open import open
from .processing_class import MyPool
from .azure_utils import upload_to_azure, download_from_azure
from functools import partial

class Downloader():
    
    def __init__(self):
        pass

    def next_chunk(self):
        pass

    def getvalue(self):
        pass

class Uploader():

    def __init__(self):
        pass

    def write(self):
        pass

    def close(self):
        pass

class Member():

    def __init__(self):
        pass

    def __len__(self):
        pass

    def create_giver(self):
        pass

    def create_receiver(self):
        pass


class AzureStorage:

    def __init__(self, container, cores):

        self.container = container
        self.cores = cores
        self.data = []
        self.chunk_size = 1024*1024

        # make connection 
        self.connect_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']
        self.transport_params = {'client': BlobServiceClient.from_connection_string(self.connect_str)}
        print("Azure made init!")

    def upload_local(self, local_path):

        print("Started upload")

        files = [os.path.join(local_path,f) for f in os.listdir(local_path)]
        target = partial(upload_to_azure, container = self.container, local_path = local_path,  cores=self.cores, transport_params=self.transport_params)
        p = MyPool(self.cores)
        p.map(target, files)
        p.close()
        p.join()

        print("Upload done!")

    def download_local(self, local_path):

        self.get_all_file_ids_paths()
        
        print("Started download!")

        target = partial(download_from_azure, container = self.container, local_path = local_path, transport_params=self.transport_params)
        p = MyPool(self.cores)
        p.map(target, self.data)
        p.close()
        p.join()


        print("Finished download!")
        

    def get_all_file_ids_paths(self):
        
        print("Creating the list of blobs")

        client = ContainerClient.from_connection_string(conn_str = self.connect_str , container_name = self.container)
        gen = client.list_blobs()

        for blob in gen:
            self.data.append(blob["name"])
        print("Made the list of blobs!")


    def make_member(self):
        pass