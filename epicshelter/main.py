from amazon_s3.amazon_s3 import AmazonS3

from google_drive import google_drive

s3 = AmazonS3("epic-shelter")
s3.upload_local("/media/mih01/Mass Storage/Transfer")