import boto3


client = boto3.resource("s3")
bucket = client.Bucket("epic-shelter")
obj = list(bucket.objects.filter(Prefix="df/"))

print(obj)