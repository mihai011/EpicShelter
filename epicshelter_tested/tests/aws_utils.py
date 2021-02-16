import os 
import datetime

def boto3_mock(service):

    if service == "s3":
        return S3Client()

    return None

dir_test = "remote_data"

class S3Client():

    def __init__(self):

        self.dir = dir_test
        self.path = os.path.join(os.getcwd(),"tests", self.dir)

    def list_objects(self, bucket):

        ret_object = {'ResponseMetadata': 
                {'RequestId': 'dummy', 'HostId': 'dummy', 'HTTPStatusCode': 200, 'HTTPHeaders': 
                {'x-amz-id-2': 'dummy', 'x-amz-request-id': 'A48E3E905674D76E', 'date': 'Tue, 16 Feb 2021 16:18:01 GMT', 'x-amz-bucket-region': 'us-east-1', 'content-type': 'application/xml', 'transfer-encoding': 'chunked', 'server': 'AmazonS3'}, 'RetryAttempts': 0}, 'IsTruncated': False, 'Marker': '', 
                'Contents': [], 'Name': 'elasticbeanstalk-us-east-1-043301319542', 'Prefix': '', 'MaxKeys': 1000, 'EncodingType': 'url'}
       
        key_object = {'Key': '', 'LastModified': '', 'ETag': '"5a642684e718afbbadaf179bfd03f0c6"', 'Size': 0, 'StorageClass': 'STANDARD', 'Owner': {'DisplayName': '', 'ID': ''}}

        for f in os.listdir(self.path):

            key_object["Key"] = f
            key_object["Size"] = os.path.getsize(os.path.join(self.path,f))

            ret_object["Contents"].append(key_object)


        return ret_object