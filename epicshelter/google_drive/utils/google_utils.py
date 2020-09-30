import io
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import os
from termcolor import colored
from googleapiclient.errors import HttpError

from functools import partial
from .processing_class import MyPool
import json
import ntpath
import magic
import socket

def convert_bytes(b, scales):
    return b/(1024**scales)

def read_in_chunks(file_object, chunk_size=1024):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def download_file_or_folder(item, drive_service, path, google_types):
    

    file_id = item['id'] 
    item_path = os.path.join(path,item['name'])

    if item["mimeType"] == "application/vnd.google-apps.folder":

        if not os.path.exists(item_path):
            os.makedirs(item_path)

        query = "'"+file_id+"' in parents and 'me' in owners and trashed=false"
        try:
            children_response = drive_service.files().list(q=query,
                        fields='files(id, name, mimeType)').execute()
        except HttpError as e:
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

        p.close()
        p.join()
        
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
                    data = fh.getvalue()
                    fh.truncate(0)
                    fh.seek(0)
                    f.write(data)
            fh.close()
            print(colored(item_path, 'green'))
        except HttpError as e:
            reason = e._get_reason()
            print(reason)
            if reason == "":
                return None
            if reason.startswith("User Rate Limit Exceeded"):
                print(colored(str(item['name']) + " User Rate Limit Exceeded","red"))
                return item
            if reason.startswith("Request range not satisfiable"):
                print(colored(str(item['name']) +" Request range not satisfiable","red"))
                return None
            return None
        except IsADirectoryError as e:
            return item


def upload_file_or_folder(path, drive_service, parent_id):


    if os.path.isdir(path):
        folder_name = ntpath.basename(path)

        if parent_id == None:

            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
        else:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents' :[parent_id]
            }
        try:
            file = drive_service.files().create(body=file_metadata,
                                        fields='id').execute()
        except HttpError as e:
            if e.resp.status == 416:
                return None
            return path

        folder_id = file.get("id")
        children = [os.path.join(path,p) for p in os.listdir(path)]
        p = MyPool(12)
        target = partial(upload_file_or_folder, drive_service=drive_service, parent_id=folder_id)
        remaining = p.map(target, children)
        remaining = list(filter(lambda x: x!=None, remaining))
        while len(remaining) != 0:
            remaining = p.map(target, remaining)
            remaining = list(filter(lambda x: x!=None, remaining))
            if len(remaining) == 1:
                print(remaining[0])
        p.close()
        p.join()
        print(path) 

    elif os.path.isfile(path):

        try:
            mt = magic.Magic(mime=True)
            mt = mt.from_file(path)
            file_name = ntpath.basename(path)
            if parent_id == None:
                file_metadata = {'name': file_name,
                    'mimeType': mt
                    }
            else:
                file_metadata = {'name': file_name,
                    'parents' :[parent_id],
                    'mimeType': mt
                    }
            
            fh = open(path,"rb+")
            media = MediaIoBaseUpload(fh,mimetype=mt,
                chunksize=6024*1024, resumable=True)

            request = drive_service.files().create(body=file_metadata,
                                                media_body=media,
                                                fields='id').execute()

            fh.close()
            print(path)
        except HttpError as e:
            if e.resp.status == 416:
                return None
            if e.resp.status in [403, 404, 500, 512]:
                print("error:"+str(e)+":"+path)
            return path
        except IsADirectoryError as e:
            return path
        except socket.timeout as e:
            return path

def delete_file(file,drive_service):

    try:
        drive_service.files().delete(fileId=file['id']).execute()
        print(file['name'])
    except HttpError as e:
        if e.resp.status == 404:
            return None
        if e.resp.status == 403:
            return None
        return file

def get_file_path(file, drive_service):

        id = file['id']

        tree = []  # Result
        while True:
            try:
                file = drive_service.files().get(fileId=id, fields='id, name, parents').execute()
                parent = file.get('parents')
                if parent:
                    while True:
                        folder = drive_service.files().get(
                            fileId=parent[0], fields='id, name, parents').execute()
                        parent = folder.get('parents')
                        if parent is None:
                            break
                        tree.append(folder.get('name'))

                break
            except HttpError as e:
                if e.resp.status == 416:
                    return None
                


        tree.reverse()
        tree.append(file["name"])
        path = os.path.join(*tree)
        
        return [path,file['id']]
