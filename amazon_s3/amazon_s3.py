import sys
import os

import boto3
from processing_class import MyPool
from functools import partial

from amazon_utils import upload_to_s3

class AmazonS3():
    
    def __init__(self, bucket):
        
        self.bucket = bucket

    def upload_local(self, local_path):

        print("Started upload")
        files = [os.path.join(local_path,f) for f in os.listdir(local_path)]
        target = partial(upload_to_s3, bucket = self.bucket, local_path = local_path)
        p = MyPool(12)
        p.map(target, files)
        p.close()

        print("Upload done!")




if __name__ == "__main__":

    s3 = AmazonS3("epic-shelter")

    s3.upload_local("/media/mih01/Mass Storage")

