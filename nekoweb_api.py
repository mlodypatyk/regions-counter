import requests
import os
from nekoweb_secrets import *

api_url = "https://nekoweb.org/api/"

def create_folder(folder_name):
    payload = f'isFolder=true&pathname={os.path.join(BASE_PATH, folder_name)}'
    headers = {
        "Authorization": API_KEY,
        "content-type": "application/x-www-form-urlencoded"
    }
    print(f'Creating remote folder for {config['country']}')
    response = requests.request("POST", api_url+'files/create', data=payload, headers=headers)
    return response

def upload_file(path, files):
    headers = {
        "Authorization": API_KEY
    }
    data = {
        "pathname": os.path.join(BASE_PATH, path)
    }
    response = requests.request("POST", api_url+'files/upload', headers=headers, data=data, files=files)
    return response

def get_folder(path):
    querystring = {
        "pathname": path
    }

    headers = {
        "Authorization": API_KEY
    }

    response = requests.request("GET", api_url+'files/readfolder', headers=headers, params=querystring)

    return response

def get_limits():
    headers = {
        "Authorization": API_KEY
    }
    response = requests.request("GET", api_url + 'files/limits', headers=headers)
    return response