from .processing_class import MyPool
from functools import partial
from  smart_open import open as open_azure

import sys
import os

def upload_to_azure(item, container, local_path, cores, transport_params):

    if os.path.isdir(item):

        files = [os.path.join(item,f) for f in os.listdir(item)]
        target = partial(upload_to_azure, container=container, local_path=local_path, cores=cores, transport_params=transport_params)
        p = MyPool(cores)
        p.map(target, files)
        p.close()
        p.join()

    else:
        
        key = os.path.relpath(item, local_path)
        azure_path = os.path.join("azure://", container, key)

        with open_azure(azure_path, 'wb', transport_params=transport_params) as azure_in:
            with open(os.path.join(local_path, key)) as local:
                try:
                    b = local.read()
                    azure_in.write(bytes(b, 'utf-8'))
                except Exception as e :
                    print(key, e)
                local.close()
            azure_in.close()

        
def download_from_azure(item, container, local_path, transport_params):

    azure_path = os.path.join("azure://", container, item)
    local_path = os.path.join(local_path, item)

    dir_path = os.path.dirname(local_path)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    with open_azure(azure_path, "rb", transport_params=transport_params) as a_out:
        with open(local_path, "wb+") as f_in:
            f_in.write(a_out.read())