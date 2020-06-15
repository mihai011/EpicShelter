import sys
import os

import boto3


from .utils.processing_class import MyPool
from .utils.amazon_utils import *

from functools import partial
import threading

from tqdm import tqdm
from time import sleep

class AmazonS3():
    
    def __init__(self, bucket, cores):
        
        self.bucket = bucket
        self.client = boto3.client("s3")
        self.cores = cores

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

if __name__ == "__main__":

    s3 = AmazonS3("epic-shelter")
    s3.upload_local("/media/mih01/Mass Storage/Transfer")

