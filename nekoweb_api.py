import requests
import os
import time
from nekoweb_secrets import *

api_url = "https://nekoweb.org/api/"

def create_folder(folder_name):
    payload = f'isFolder=true&pathname={os.path.join(BASE_PATH, folder_name)}'
    headers = {
        "Authorization": API_KEY,
        "content-type": "application/x-www-form-urlencoded"
    }
    response = requests.request("POST", api_url+'files/create', data=payload, headers=headers)
    if response.status_code == 429:
        print('sleeping because too many request')
        time.sleep(60)
        return create_folder(folder_name)
    return response

def upload_file(path, files):
    headers = {
        "Authorization": API_KEY
    }
    data = {
        "pathname": os.path.join(BASE_PATH, path)
    }
    response = requests.request("POST", api_url+'files/upload', headers=headers, data=data, files=files)
    if response.status_code == 429:
        print('sleeping because too many request')
        time.sleep(60)
        return upload_file(path, files)
    return response

def get_folder(path):
    querystring = {
        "pathname": path
    }

    headers = {
        "Authorization": API_KEY
    }

    response = requests.request("GET", api_url+'files/readfolder', headers=headers, params=querystring)
    if response.status_code == 429:
        print('sleeping because too many request')
        time.sleep(60)
        return get_folder(path)

    return response

def get_limits():
    headers = {
        "Authorization": API_KEY
    }
    response = requests.request("GET", api_url + 'files/limits', headers=headers)
    return response
