import io
from googleapiclient.http import MediaIoBaseDownload
import os
from termcolor import cprint
from googleapiclient.errors import HttpError


def convert_bytes(b, scales):
    return b/(1024**scales)

def get_google_types():
    return open("google_types.data").read().split("\n")

def download_file_or_folder(item, drive_service,path, google_types):

    file_id = item['id'] 
    item_path = os.path.join(path,item['name'])

    if item["mimeType"] == "application/vnd.google-apps.folder":

        if not os.path.exists(item_path):
            os.makedirs(item_path)
            #cprint('Directory {} made!!!'.format(item_path), 'green', 'on_white')

        query = "'"+file_id+"' in parents"
        children_response = drive_service.files().list(q=query,
                    fields='files(id, name, mimeType)').execute()
        children =  children_response.get('files',[])

        for c in children:
            download_file_or_folder(c, drive_service, item_path, google_types)
    
    try:
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        if item['mimeType'] in google_types:
            return 
        with open(item_path, "wb") as f:
            while done is False:
                status, done = downloader.next_chunk()
                f.write(fh.getvalue())
    except HttpError as e:
        print(item["mimeType"])
        return
    except IsADirectoryError as e:
        print(item['mimeType'], item['name'])