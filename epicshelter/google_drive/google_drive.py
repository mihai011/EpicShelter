from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from functools import partial
from tqdm import tqdm

import matplotlib.pyplot as plt

import json
import os
import requests

from .utils.google_utils import *
from .utils.processing_class import MyPool

SCOPES = ['https://www.googleapis.com/auth/drive',\
    'https://www.googleapis.com/auth/drive.install',\
    'https://www.googleapis.com/auth/drive.appdata']


class Google_Drive():

    g_types = open( "google_types.data").read().split("\n")

    def __init__(self, credentials_file):
        """Verifiy credentials and construct and create credentials if necessary"""

        self.creds = None
        if os.path.exists("token.pickle"):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds,token)

        self.service = build('drive', 'v3', credentials=self.creds)

        self.first_level = Google_Drive.retrieve_drive_first_level(self.service)

        print("Init made!")

    def get_files(self, page_size):
        
        items = []

        if page_size == 0:
            page_token = None
            
            while True:
                
                response = self.service.files().list(fields='nextPageToken, files(id, name, size, mimeType)',
                    pageToken=page_token).execute()

                items += response.get('files', [])
                
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break

        else:

            results = self.service.files().list(pageSize=page_size, 
                fields="nextPageToken, files(id, name)").execute()

            items = results.get('files', [])

        return items


    def show_full_stats(self):
        """ getting some stats about the current state of the drive """

        stats = {}
        total = 0
        page_token = None

        while True:

            response = self.service.files().list(fields='nextPageToken, files(size, mimeType)',
                    pageToken=page_token).execute()

            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

            for f in response.get('files', []):

                if 'size' in f:
                    if f['mimeType'] not in stats:
                        stats[f['mimeType']] = int(f['size'])
                    else:
                        stats[f['mimeType']] += int(f['size'])

                    total += int(f['size'])

        for s in stats.keys():
            stats[s] = (stats[s]/total) * 100

        print(stats)
        plt.xticks(rotation='vertical')
        plt.bar(stats.keys(), stats.values(), 1.0, color='g')
        plt.show()

    @staticmethod
    def retrieve_drive_first_level(service):
        """getting the first level of the drive file structure"""

        all_items = []
        page_token = None

        while True:
            
            response = service.files().list(q="'me' in owners and trashed=false",
                fields='nextPageToken, files(id, name, mimeType)',
                pageToken=page_token).execute()

            all_items += response.get('files', [])
            
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        
        page_token = None

        while True:

            response = service.files().list(q="mimeType='application/vnd.google-apps.folder'",
                pageToken=page_token).execute()

            children = []
            for directory in response.get('files',[]):

                children_response = service.files().list(q="'"+directory['id']+"' in parents",
                    fields='files(id, name)').execute()
                children += [r['id'] for r in children_response.get('files',[])]
                

            all_items = [a for a in all_items if a['id'] not in children]
            page_token = response.get('nextPageToken',None)

            if page_token == None:
                break

        #first-level only files, including directors, without google types
        all_items = [a for a in all_items if a['mimeType'] not in Google_Drive.g_types]


        return all_items


    def download_local(self, path):
        """Download a list of files with id's at a designated path"""
        list_id = self.first_level
        print("Started downloading!")
        p = MyPool(12)
        target = partial(download_file_or_folder,google_types=Google_Drive.g_types, drive_service=self.service, path=path)
        data = p.map(target, list_id)
        data = list(filter(lambda x: x!=None, data))
        while len(data) !=  0:
            data = p.map(target, data)
            data = list(filter(lambda x: x!=None, data))
        p.close()
        p.join()
        print("Download finished!")


    def upload_local(self, local_path):
        """Upload all the contents from a local path """


        files = [os.path.join(local_path,f) for f in os.listdir(local_path)]
        target = partial(upload_file_or_folder,drive_service = self.service,parent_id=None)
        p = MyPool(12)
        data = p.map(target, files)
        data = list(filter(lambda x: x!=None, data))
        while len(data) !=  0:
            data = p.map(target, data)
            data = list(filter(lambda x: x!=None, data))
            if len(data) == 1:
                print(data[0])
        p.close()
        p.join()
        print("Upload finished!")

        
    def delete_all_files(self):

        page_token = None
        files = []

        while True:

            response = self.service.files().list(fields='nextPageToken, files(id,name)',
                    pageToken=page_token).execute()

            page_token = response.get('nextPageToken', None)
            files += response.get('files',[])

            if page_token is None:
                break
            
            
        target = partial(delete_file,drive_service = self.service)
        p = MyPool(12)
        data = p.map(target, files)
        data = list(filter(lambda x: x!=None, data))
        while len(data) !=  0:
            data = p.map(target, data)
            data = list(filter(lambda x: x!=None, data))
            print(len(data))
        p.close()
        p.join()

        print("Delete all finished!")

    def get_all_file_ids_paths(self):

        all_items = []
        page_token = None

        while True:
            
            response = self.service.files().list(q="'me' in owners and trashed=false",
                fields='nextPageToken, files(id, name, mimeType)',
                pageToken=page_token).execute()

            all_items += response.get('files', [])
            
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        all_items = list(filter(lambda item: item["mimeType"] != "application/vnd.google-apps.folder", all_items))

        target = partial(get_file_path,drive_service = self.service)
        p = MyPool(3)
        data = p.map(target, all_items)
        data = list(filter(lambda x: x!=None, data))
        p.close()
        p.join()
        self.current_data = data

    def upload_file(self, path):

        access_token = self.creds.token
        filename = path

        filesize = os.path.getsize(filename)

        # 1. Retrieve session for resumable upload.

        headers = {"Authorization": "Bearer "+access_token, "Content-Type": "application/json"}
        params = {
            "name": "br2049.mkv",
            "mimeType": "video/x-matroska"
        }
        r = requests.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable",
            headers=headers,
            data=json.dumps(params)
        )
        location = r.headers['Location']

        # 2. Upload the file.
        chunksize = 262144*64
        prev = 0
        with open(filename,'rb') as f:
            for piece in read_in_chunks(f,chunk_size=chunksize):
                
                offset = prev+len(piece)-1
                headers = {"Content-Range": "bytes "+str(prev)+"-" + str(offset) + "/" + str(filesize)}
                prev = offset+1
                r = requests.put(
                    location,
                    headers=headers,
                    data=piece
                )
                print(r.text)
        

    def make_member(self):

        class Uploader():

            def __init__(self, creds, packet, service):

                first_level = Google_Drive.retrieve_drive_first_level(service)

                while True:

                    try:
                        path = packet["path"]
                        print(path)

                        self.filesize = packet['filesize']
                        self.path = path.split("/")

                        last_id = None
                        access_token = creds.token

                        level = first_level
                        
                        
                        for i in range(len(self.path)-1):
                            found = False
                            for l in level:
                            
                                if self.path[i] == l['name'] and l['mimeType'] == 'application/vnd.google-apps.folder':
                                    found=True
                                    children_response = service.files().list(q="'"+l['id']+"' in parents",
                                        fields='files(id, name, mimeType)').execute()
                                    children = children_response.get('files',[])
                                    last_id = l['id']
                                    break

                            if found:
                                level = children
                            else:
                                if last_id == None:

                                    file_metadata = {
                                        'name': self.path[i],
                                        'mimeType': 'application/vnd.google-apps.folder'
                                    }
                                else:
                                     file_metadata = {
                                        'name': self.path[i],
                                        'mimeType': 'application/vnd.google-apps.folder',
                                        'parents':[last_id]
                                    }
                                file = service.files().create(body=file_metadata,
                                                                    fields='id').execute()

                                last_id = file.get('id')

                                

                        if last_id == None:
                            params = {
                            "name": self.path[-1],
                            "mimeType": 'application/octet-stream',
                            }
                        else:
                            params = {
                            "name": self.path[-1],
                            "mimeType": 'application/octet-stream',
                            "parents":[last_id]
                        }

                        headers = {"Authorization": "Bearer "+access_token, "Content-Type": "application/json"}
                        
                        r = requests.post(
                            "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable",
                            headers=headers,
                            data=json.dumps(params)
                        )

                        self.location = r.headers['Location']
                        self.prev = 0

                        break
                    except Exception as e:
                        print(e)

                    

                
            def write(self,piece):
                
                offset = self.prev+len(piece)-1
                headers = {"Content-Range": "bytes "+str(self.prev)+"-" + str(offset) + "/" + str(self.filesize)}
                self.prev = offset+1

                r = requests.put(
                    self.location,
                    headers=headers,
                    data=piece
                )
                

            def close(self):
                pass



        class Downloader():

            def __init__(self, fh, downloader):

                self.fh = fh
                self.downloader = downloader

            def next_chunk(self):

                return self.downloader.next_chunk()

            def getvalue(self): 

                data = self.fh.getvalue()
                self.fh.truncate(0)
                self.fh.seek(0)

                return data


            def close(self):

                self.fh.close()
                


        class Member():

            def __init__(self, data, service, creds):
                
                self.data = data
                self.service = service
                self.creds = creds

            def __len__(self):
                
                return len(self.data)

            def create_giver(self,index):

                request = self.service.files().get_media(fileId=self.data[index][1])

                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)

                package = {"path":self.data[index][0]}
                
                return Downloader(fh, downloader) , package

            def create_receiver(self,packet):

                return Uploader(self.creds, packet, self.service)

        self.get_all_file_ids_paths()


        return Member(self.current_data, self.service, self.creds)

if __name__ == "__main__":

    g = Google_Drive()
    g.show_full_stats()
    #path = "/media/mih01/Mass Storage/Transfer"
    #g.download_local(path)
    


