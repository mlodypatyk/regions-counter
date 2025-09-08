import requests
import os
import time
from nekoweb_secrets import *
import json

class NekowebApi:

    def __init__(self):

        self.api_url = "https://nekoweb.org/api/"
        response = self.get_limits()
        response_obj = json.loads(response.text)
        self.remaining = response_obj['general']['remaining']
        self.reset = response_obj['general']['reset']
        print(self.reset)

    def create_folder(self, folder_name):
        payload = f'isFolder=true&pathname={os.path.join(BASE_PATH, folder_name)}'
        headers = {
            "content-type": "application/x-www-form-urlencoded"
        }
        return self.__request__("POST", self.api_url+'files/create', data=payload, headers=headers)

    def upload_file(self, path, files):
        data = {
            "pathname": os.path.join(BASE_PATH, path)
        }
        return self.__request__("POST", self.api_url+'files/upload', data=data, files=files)
        

    def get_folder(self, path):
        querystring = {
            "pathname": path
        }
        return self.__request__("GET", self.api_url+'files/readfolder', params=querystring)

    
    def __request__(self, method, url, headers = None, params = None, data = None, files = None):
        local_headers = {
            "Authorization": API_KEY
        }
        if headers:
            local_headers.update(headers)
        if self.remaining == 0:
            print(f'Sleeping for {self.reset} for rate limit')
            time.sleep(self.reset)
        response = requests.request(method, url, headers=local_headers, params=params, data=data, files=files)
        if 'ratelimit-remaining' in  response.headers:
            self.remaining = int(response.headers['ratelimit-remaining'])
        if 'ratelimit-reset' in response.headers:
            self.reset = int(response.headers['ratelimit-reset'])
        return response
        
        

    def get_limits(self):
        headers = {
            "Authorization": API_KEY
        }
        response = requests.request("GET", self.api_url + 'files/limits', headers=headers)
        return response
