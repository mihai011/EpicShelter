from processing_class import MyPool
from functools import partial

import sys
import os
import boto3

client = boto3.client("s3")

def upload_to_s3(item,bucket,local_path):

    if os.path.isdir(item):

        files = [os.path.join(item,f) for f in os.listdir(item)]
        target = partial(upload_to_s3, bucket=bucket, local_path=local_path)
        p = MyPool(12)
        p.map(target, files)
        p.close()

    else:
        key = os.path.relpath(item, local_path)
        client.upload_file(item, bucket, key)
        print(key)

def download_to_s3(item, bucket, local_path):

    filename = os.path.join(local_path,item)

    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            pass
    
    print(filename)
    with open(filename, 'wb+') as data:
        client.download_fileobj(bucket, item, data)
        

