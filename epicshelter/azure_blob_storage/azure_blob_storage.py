import os 
from azure.storage.blob import BlobServiceClient
from smart_open import open
from .processing_class import MyPool
from .azure_utils import upload_to_azure
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
        connect_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']
        self.transport_params = {'client': BlobServiceClient.from_connection_string(connect_str)}


    def upload_local(self, local_path):

        print("Started upload")

        files = [os.path.join(local_path,f) for f in os.listdir(local_path)]
        target = partial(upload_to_azure, container = self.container, local_path = local_path,  cores=self.cores, transport_params=self.transport_params)
        p = MyPool(self.cores)
        p.map(target, files)
        p.close()
        p.join()

        print("Upload done!")

    def download_local(self):
        pass

    def get_all_file_ids_paths():
        pass

    def make_member(self):
        pass