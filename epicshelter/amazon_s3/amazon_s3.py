import sys
import os

import boto3
from smart_open import open as s3_open


from .utils.processing_class import MyPool
from .utils.amazon_utils import *

from functools import partial
import threading

from tqdm import tqdm
from time import sleep

class Downloader():

    def __init__(self, bucket, key, chunk_size):

        self._fd = s3_open('s3://'+os.path.join(bucket,key), 'rb', transport_params={'session': boto3.session.Session(),\
            'buffer_size': chunk_size})
        self.chunk_size = chunk_size
        self.current_data = None

    def next_chunk(self):
        
        data = self._fd.read(self.chunk_size)
        if len(data) < self.chunk_size:
            self.current_data = data
            return True, True

        self.current_data = data
        
        return True, False

    def getvalue(self):

        return self.current_data

class Uploader():

    def __init__(self, bucket, packet):

        key = packet["path"]

        s3 = boto3.client('s3')
        self.bucket = bucket
        self.key = key
        s3.put_object(Bucket=self.bucket,Key=self.key)

        self._fd = s3_open('s3://'+os.path.join(self.bucket,self.key), 'wb', transport_params={'session': boto3.session.Session()})

    def write(self, data):

        self._fd.write(data)

    def close(self):

        self._fd.close()

        
class Member():

    def __init__(self, bucket, data):
        
        self.bucket = bucket
        self.data = data

    def __len__(self):
        
        return len(self.data)

    def create_giver(self, index):

        downloader = Downloader(self.bucket, self.data[index], 262144*256)

        s3 = boto3.resource('s3')
        s3_object = s3.Object(self.bucket, self.data[index])
        filesize = s3_object.content_length

        package = {"path":self.data[index],
                    "filesize": filesize
            }

        return downloader, package


    def create_receiver(self, packet):

        return Uploader(self.bucket, packet)

class AmazonS3():
    
    def __init__(self, bucket, cores):
        
        self.bucket = bucket
        self.client = boto3.client("s3")
        self.cores = cores
        self.data = []
        self.chunk_size = 1024*1024

        self.get_all_file_ids_paths()

    def upload_local(self, local_path):

        print("Started upload")

        files = [os.path.join(local_path,f) for f in os.listdir(local_path)]
        target = partial(upload_to_s3, bucket = self.bucket, local_path = local_path)
        p = MyPool(self.cores)
        p.map(target, files)
        p.close()
        p.join()

        print("Upload done!")

    def download_local(self, local_path):

        files = self.client.list_objects(Bucket=self.bucket)
        paths = [f["Key"] for f in files["Contents"]]
        target = partial(download_to_s3, bucket=self.bucket, local_path=local_path)
        
        download_thread = threading.Thread(target=download_keys,args=[target,paths,self.cores, self.bucket])
        download_thread.start()

    def delete_all_files(self):

        s3 = boto3.resource('s3')
        bucket = s3.Bucket(self.bucket)
        bucket.objects.all().delete()
        print("Delete all done!")

    def get_all_file_ids_paths(self):

        self.data = []
        resp = self.client.list_objects_v2(Bucket=self.bucket)
        if "Contents" not in resp:
            return
        for obj in resp['Contents']:
            self.data.append(obj['Key'])

        

    def make_member(self):

        
        return Member(self.bucket,self.data)

if __name__ == "__main__":

    s3 = AmazonS3("epic-shelter")
    s3.upload_local("/media/mih01/Mass Storage/Transfer")

