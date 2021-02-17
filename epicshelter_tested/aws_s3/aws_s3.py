import boto3
from botocore.client import ClientError


class S3():

    def __init__(self):

        self.client = boto3.client("s3")

    def list_objects(self, bucket=None):

        if bucket == None:
            raise ValueError("Bucket is None!")

        data = self.client.list_objects(Bucket=bucket)

        keys = []

        for k in data["Contents"]:
            keys.append(k["Key"])
        
        return keys

    def download_fileobj(self, Bucket=None,Key=None, target=None):

        if Bucket == None:
            raise ValueError("Bucket is None!")

        if Key == None:
            raise ValueError("Key is None!")

        if target == None:
            raise ValueError("Target is None!")

        with open(target, "wb+") as data:
            self.client.download_fileobj(Bucket, Key, data)
