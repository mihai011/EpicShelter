import io
from googleapiclient.http import MediaIoBaseDownload

def convert_bytes(b, scales):
    return b/(1024**scales)

def download_file_or_folder(id, drive_service,path):

    file_id = id 
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))