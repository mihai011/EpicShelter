from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io
import boto3 
from google_drive.google_drive import Google_Drive
from smart_open import open as s3_open

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
            f.write(fh.getvalue())


if __name__ == "__main__":

    google_to_amazon("1fdhoNqOGBlWy6zV5euhuBahmAfbXMmCg")
