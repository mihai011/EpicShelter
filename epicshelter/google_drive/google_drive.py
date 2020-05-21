from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from functools import partial
from tqdm import tqdm

import matplotlib.pyplot as plt

from .utils.google_utils import *
from .utils.processing_class import MyPool

SCOPES = ['https://www.googleapis.com/auth/drive',\
    'https://www.googleapis.com/auth/drive.install',\
    'https://www.googleapis.com/auth/drive.appdata']


class Google_Drive():

    def __init__(self):
        """Verifiy credentials and construct and create credentials if necessary"""

        self.creds = None
        if os.path.exists("token.pickle"):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('test.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds,token)

        self.service = build('drive', 'v3', credentials=self.creds)
        self.g_types = open("google_types.data").read().split("\n")

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

        
        plt.xticks(rotation='vertical')
        plt.bar(stats.keys(), stats.values(), 1.0, color='g')
        plt.show()

    def retrieve_drive_first_level(self):
        """getting the first level of the drive file structure"""

        print("Getting Drive first level!")
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
        
        page_token = None

        while True:

            response = self.service.files().list(q="mimeType='application/vnd.google-apps.folder'",
                pageToken=page_token).execute()

            children = []
            for directory in response.get('files',[]):

                children_response = self.service.files().list(q="'"+directory['id']+"' in parents",
                    fields='files(id, name)').execute()
                children += [r['id'] for r in children_response.get('files',[])]
                pass

            all_items = [a for a in all_items if a['id'] not in children]
            page_token = response.get('nextPageToken',None)

            if page_token == None:
                break

        #first-level only files, including directors, without google types
        all_items = [a for a in all_items if a['mimeType'] not in self.g_types]

        print("Got first level!")
        return all_items


    def download_local(self, path):
        """Download a list of files with id's at a designated path"""
        list_id = self.retrieve_drive_first_level()
        print("Started downloading!")
        p = MyPool(12)
        target = partial(download_file_or_folder,google_types=self.g_types, drive_service=self.service, path=path)
        data = p.map(target, list_id)
        data = list(filter(lambda x: x!=None, data))
        while len(data) !=  0:
            data = p.map(target, data)
            data = list(filter(lambda x: x!=None, data))
        p.close()
        print("Download finished!")


    def upload_local(self, local_path):
        """Upload all the contents from a local path """


        files = [os.path.join(local_path,f) for f in os.listdir(local_path)]
        target = partial(upload_to_drive)
        p = MyPool(12)
        p.map(target, files)
        p.close()


if __name__ == "__main__":

    g = Google_Drive()
    #g.show_full_stats()
    #path = "/media/mih01/Mass Storage/Transfer"
    #g.download_local(path)
    


