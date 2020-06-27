from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io
import boto3 
from google_drive.google_drive import Google_Drive
from smart_open import open as s3_open
import ntpath
import requests
import json
import magic


def google_to_amazon(file_id):
    
    gd = Google_Drive("credentials.json", "google_types.data")
    drive_service = gd.service

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    s3 = boto3.client('s3')
    s3.put_object(Bucket="epic-shelter",Key="test.mp4")
    done=False
    with s3_open('s3://epic-shelter/test.mp4', 'wb', transport_params={'session': boto3.session.Session()}) as f:
        while done is False:
            status, done = downloader.next_chunk()
            fh.truncate(0)
            fh.seek(0)
            f.write(fh.getvalue())

def amazon_to_google(key):

    chunk_size = 262144*64
    gd = Google_Drive("credentials.json", "google_types.data")
    access_token = gd.creds.token


    s3 = boto3.resource('s3')
    s3_object = s3.Object('epic-shelter', key)
    filesize = s3_object.content_length


    amazon = s3_open('s3://epic-shelter/'+key, 'rb', transport_params={'session': boto3.session.Session()})

    headers = {"Authorization": "Bearer "+access_token, "Content-Type": "application/json"}
    params = {
        "name": ntpath.basename(key),
        "mimeType": 'application/octet-stream'
    }
    r = requests.post(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable",
        headers=headers,
        data=json.dumps(params)
    )

    location = r.headers['Location']
    prev = 0

    while True:

        piece = amazon.read(chunk_size)
        if not piece:
            break
            
        offset = prev+len(piece)-1
        headers = {"Content-Range": "bytes "+str(prev)+"-" + str(offset) + "/" + str(filesize)}
        print(prev,offset)
        prev = offset+1
        r = requests.put(
            location,
            headers=headers,
            data=piece
        )
        print(r.text)
            



            

if __name__ == "__main__":

    #google_to_amazon("1fdhoNqOGBlWy6zV5euhuBahmAfbXMmCg")
    amazon_to_google("GitHub/slamyc/data/test.mp4")
