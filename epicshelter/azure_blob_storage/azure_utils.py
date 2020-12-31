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

        
            

        