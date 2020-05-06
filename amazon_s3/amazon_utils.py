from processing_class import MyPool
from functools import partial

import sys
import os
import boto3

client = boto3.client("s3")
s3 = boto3.resource('s3')

def get_size_folder(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

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

    s3.meta.client.download_file(bucket, item, filename)


def get_bucket_size(bucket_name):

    total_size = 0
    bucket = boto3.resource('s3').Bucket(bucket_name)
    for object in bucket.objects.all():
        total_size += object.size
    return total_size



def download_keys(target, paths, cores, bucket):

    size = get_bucket_size(bucket)
    print("Started downloading: "+ str(size/1024/1024/1024) + " GB")
    p = MyPool(cores)
    p.map(target, paths)
    p.close()
    print("Download ended!")