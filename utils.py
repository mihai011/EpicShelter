import io
from googleapiclient.http import MediaIoBaseDownload
import os
from termcolor import cprint
from googleapiclient.errors import HttpError

from functools import partial
from processing_class import MyPool
import json

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

        query = "'"+file_id+"' in parents and 'me' in owners and trashed=false"
        try:
            children_response = drive_service.files().list(q=query,
                        fields='files(id, name, mimeType)').execute()
        except HttpError as e:
            cprint('{}'.format(e), 'red', 'on_white')
            if e.resp.status == 416:
                return None
            return item
        children =  children_response.get('files',[])
        
        p = MyPool(12)
        target = partial(download_file_or_folder,google_types=google_types, drive_service=drive_service, path=item_path)
        remaining = p.map(target, children)
        remaining = list(filter(lambda x: x!=None, remaining))
        while len(remaining) != 0:
            remaining = p.map(target, remaining)
            remaining = list(filter(lambda x: x!=None, remaining))
        #p.join()
        p.close()
        
        """
        for c in children:
            download_file_or_folder(c, drive_service, item_path, google_types)
        """
    else:

        try:
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            if item['mimeType'] in google_types:
                return 
            with open(item_path, "wb+") as f:
                while done is False:
                    status, done = downloader.next_chunk()
                    f.write(fh.getvalue())
            fh.close()
        except HttpError as e:
            cprint('{}'.format(e), 'green', 'on_white')
            if e.resp.status == 416:
                return None
            return item
        except IsADirectoryError as e:
            cprint('{}|{}'.format(item['mimeType'],e), 'red', 'on_grey')