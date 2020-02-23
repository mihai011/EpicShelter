from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from functools import partial

import matplotlib.pyplot as plt

from utils import convert_bytes, download_file_or_folder

SCOPES = ['https://www.googleapis.com/auth/drive.file']

from multiprocessing import Pool


class Google_Drive():

    def __init__(self):

        
        if os.path.exists("token.pickle"):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds,token)

        self.service = build('drive', 'v3', credentials=self.creds)

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

        all_items = []

        page_token = None

        while True:
            
            response = self.service.files().list(fields='nextPageToken, files(id, name)',
                pageToken=page_token).execute()

            all_items += [r['id'] for r in response.get('files', [])]
            
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

            all_items = [a for a in all_items if a not in children]
            page_token = response.get('nextPageToken',None)

            if page_token == None:
                break

        #first-level only files, including directors
        return all_items


    def download_recursively(self, list_id):

        p = Pool(12)
        target = partial(download_file_or_folder, drive_service=self.service, path="drive")
        p.map(target, list_id)
                
    

if __name__ == "__main__":

    g = Google_Drive()

    first_level = g.retrieve_drive_first_level()
    
    g.download_recursively(first_level)
    


