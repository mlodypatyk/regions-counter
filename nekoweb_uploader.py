import os
import requests
import json
import time

import nekoweb_api
from nekoweb_secrets import *
from dbsecrets import *
from localconfig import configs
from config_loader import get_local_configs
import mysql.connector



if __name__ == '__main__':
    mydb = None
    if SECRET_PASSWORD:
        mydb = mysql.connector.connect(host = SECRET_HOST, user = SECRET_USER, database = SECRET_DATABASE, password = SECRET_PASSWORD)
    else:
        mydb = mysql.connector.connect(host = SECRET_HOST, user = SECRET_USER, database = SECRET_DATABASE)
    cursor = mydb.cursor()

    limits = nekoweb_api.get_limits()
    print(limits.text)

    response = nekoweb_api.get_folder(BASE_PATH)

    directory_data = json.loads(response.text)

    for config in get_local_configs(cursor, lambda x: print(x)) + configs:
        country = config['country']
        path_name = config['path_name']
        folders = [token['name'] for token in directory_data if token['dir']]
        if country not in folders:
            print(f'Creating remote folder for {country}')
            response = nekoweb_api.create_folder(country)
            
            if response.ok:
                directory_data.append({'name': country, 'dir': True})
            else:
                print('Error when creating folder')
                print(response.text)
                raise Exception()
        file_path = os.path.join(country, f'{path_name}.html')
        files = {'files': open(os.path.join('output', file_path), 'rb')}
        print(f'Uploading {country}/{file_path}')
        response = nekoweb_api.upload_file(country, files)
        if response.ok:
            print("Succesfully uploaded")
        else:
            print("mi bombo")
            print(response.text)

    other_files = ['index.html', 'log.html']
    for file in other_files:
        file_path = f'output/{file}'
        files = {"files": open(file_path, 'rb')}
        print(f'Uploading {file}')
        response = nekoweb_api.upload_file('', files)
        if response.ok:
            print("Succesfully uploaded")
        else:
            print("mi bombo")
            print(response.text)

        
        