import os
from azure.storage.blob import BlobServiceClient
from smart_open import open

connect_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']

transport_params = {'client': BlobServiceClient.from_connection_string(connect_str)}

with open("azure://test/test/a/b/c/something_good_to_look_at.txt", "wb", transport_params=transport_params) as f:
    f.write(b"test")