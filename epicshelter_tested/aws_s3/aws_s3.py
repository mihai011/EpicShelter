import boto3

class S3():

    def __init__(self):

        self.client = boto3.client("s3")

    def list_objects(self, bucket = None):

        if bucket == None:
            raise ValueError("Bucket is none")
        
        data = self.client.list_objects(bucket)

        keys = []

        for k in data["Contents"]:
            keys.append(k["Key"])
        
        return keys