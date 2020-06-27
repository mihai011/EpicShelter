import json
import os
import requests

access_token = 'ya29.a0AfH6SMAtV1HcNVXCRMTuag9T0QMT4WC8E36k7mZftFy6S5j8KXHrkmbZPTeHRWwmzDy5_LJL9wLFLgXZpLktVZ1UJJ1JGWnaI7Fo4KUXqJqSMTvX3cVlti9_FqyW07EgoGkw0DZV7HGd_vEfTYspmswIRcS2QwsWxjra'  ## Please set the access token.

filename = '/home/mih011/Downloads/Introduction to Probability and Statistics 15th Edition/Introduction to Probability and Statistics 15th Edition.pdf'

filesize = os.path.getsize(filename)

# 1. Retrieve session for resumable upload.

headers = {"Authorization": "Bearer "+access_token, "Content-Type": "application/json"}
params = {
    "name": "sample.png",
    "mimeType": "image/png"
}
r = requests.post(
    "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable",
    headers=headers,
    data=json.dumps(params)
)
location = r.headers['Location']

# 2. Upload the file.

headers = {"Content-Range": "bytes 0-" + str(filesize - 1) + "/" + str(filesize)}
r = requests.put(
    location,
    headers=headers,
    data=open(filename, 'rb')
)
print(r.text)