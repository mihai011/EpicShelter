from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import matplotlib.pyplot as plt

from utils import convert_bytes

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


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


    def list_files(self, page_size):
        
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
    

if __name__ == "__main__":

    g = Google_Drive()

    g.show_full_stats()

    


